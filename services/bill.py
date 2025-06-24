from datetime import datetime
from models import Bill, Groups, Items, Assignments, Participants, Payments, Ledgers, User
from utils.error import CustomError
from flask import g as ctx
from utils.clean import clean_datetime

class BillService:
    def create_bill(self):
        ref = Bill.create_ref()

        data = {
            'bill_name': f'split_bill-{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}-{ref.id}',
            'created_by': ctx.user_id,
            'join_code': ref.id,
            'participants': [],
            'is_finalized': False,
        }

        ref.set(data)

        return ref.get().to_dict()
    
    def add_item(self, data, bill_id):
        bill = Bill(bill_id)

        if bill is None:
            raise CustomError("bill not found", 404)
        
        existing_items = bill.get_items()
        
        if existing_items != []:
            raise CustomError("items already set", 403)
        
        total_price = 0
        
        for i in data:
            item = Items.create_ref(bill.id)

            total_price += i.get('unit_price', 0) * i.get('total_quantity', 1)

            item.set({
                "name": i.get('name'),
                "unit_price": i.get('unit_price', 0),
                "total_quantity": i.get('total_quantity', 1),
            })

        bill.update({
            'total_price': total_price,
        })

        return bill.get_items()
    
    def create_completed_bill(self, args):
        ref = Bill.create_ref()

        if not args.get('group_id'):
            participant = [ctx.user_id]
            for i in args.get('participants', []):
                if i not in participant:
                    participant.append(i)
        else:
            group_ref = Groups(args['group_id'])
            group_data = group_ref.get()

            if not group_data:
                raise CustomError("group not found", 404)

            # Group will be the source of participants; no need to store them in the bill.
            participant = None  # explicitly ignore participants in bill

        split_type = args.get('split_type', 'equal')

        bill_data = {
            'bill_name': f'split_bill-{datetime.now().strftime("%Y-%m-%d-%H:%M:%S")}-{ref.id}',
            'created_by': ctx.user_id,
            'group_id': args.get('group_id', None),
            'join_code': ref.id,
            'split_type': split_type,
            'is_finalized': True,
        }

        if not args.get('group_id'):
            bill_data['participants'] = participant  # only include this when there's no group

        ref.set(bill_data)

        items = args.get('items', [])
        total_price = 0
        item_data = []
        for item in items:
            item_ref = Items.create_ref(bill_id=ref.id)

            item_data.append({
                'id': item_ref.id,
                'name': item.get('name'),
                'unit_price': item.get('unit_price'),
                'total_quantity': item.get('total_quantity', 1),
            })

            total_price += item.get('unit_price', 0) * item.get('total_quantity', 1)

            item_ref.set(item_data[-1])

            if split_type == 'by_item':
                assignments = item.get('assignments', [])

                for assignment in assignments:
                    assignment_ref = Assignments.create_ref(
                        bill_id=ref.id,
                        item_id=item_ref.id,
                        user_id=assignment.get('user_id')
                    )

                    assignment_ref.set({
                        'user_id': assignment.get('user_id'),
                        'quantity': assignment.get('quantity', 1),
                    })

        ref.update({
            'total_price': total_price,
        })

        if split_type == 'equal':
            per_person_amount = total_price / len(participant)

            for user_id in participant:
                participant_ref = Participants.create_ref(bill_id=ref.id, participant_id=user_id)
                participant_ref.create({
                    'amount_owed': per_person_amount,
                    'is_settled': False,
                })
        elif split_type == 'by_item':
            items = Bill(ref.id).get_items()
            participant_dict = {}
            for item in items:
                assignment_ref = Items(bill_id=ref.id, id=item['id']).get_assignments()

                for assignment in assignment_ref:
                    total_price_item = item['unit_price'] * assignment['quantity']
                    if assignment['user_id'] not in participant_dict:
                        participant_dict[assignment['user_id']] = total_price_item
                    else:
                        participant_dict[assignment['user_id']] += total_price_item
            for participant_id, amount in participant_dict.items():
                participant_ref = Participants.create_ref(bill_id=ref.id, participant_id=participant_id)
                participant_ref.create({
                    'amount_owed': amount,
                    'is_settled': False,
                })
        
        payments = args.get('payments', [])
        for payment in payments:
            payment_ref = Payments.create_ref(bill_id=ref.id)
            payment_ref.create({
                'amount': payment.get('amount'),
                'paid_by': payment.get('paid_by', ctx.user_id),
            })

        response = ref.get().to_dict()
        response['id'] = ref.id
        response['items'] = Bill(ref.id).get_items()
        for item in response['items']:
            item['assignments'] = Items(bill_id=ref.id, id=item['id']).get_assignments()
        response['payments'] = Bill(ref.id).get_payments()
        response['participants'] = Bill(ref.id).get_participants()
        response['ledgers'] = self.create_ledgers(bill_id=ref.id)

        return response
    
    def create_ledgers(self, bill_id):
        data = Bill(bill_id).get()

        if not data:
            raise CustomError("bill not found", 404)
        
        participants = Bill(bill_id).get_participants()
        payments = Bill(bill_id).get_payments()
        
        if not participants:
            raise CustomError("no participants in the bill", 400)
        
        if not payments:
            raise CustomError("no payments in the bill", 400)
        
        paid_data = {}
        owed_data = {}
        for payment in payments:
            paid_data[payment['paid_by']] = paid_data.get(payment['paid_by'], 0) + payment['amount']

        for participant in participants:
            owed_data[participant['participant_id']] = owed_data.get(participant['participant_id'], 0) + participant['amount_owed']
        
        net_data = {}
        for user in set(paid_data) | set(owed_data):
            paid = paid_data.get(user, 0)
            owed = owed_data.get(user, 0)

            net_data[user] = round(paid - owed, 2)

        debtors = {u: a for u, a in net_data.items() if a < 0}
        creditors = {u: a for u, a in net_data.items() if a > 0}

        ledgers = []
        for debtor, debt_amount in debtors.items():
            debt_remaining = -debt_amount
            for creditor, credit_amount in list(creditors.items()):
                if credit_amount <= 0:
                    continue
                payment = min(debt_remaining, credit_amount)
                ledgers.append({
                    "debtor_user_id": debtor,
                    "creditor_user_id": creditor,
                    "amount": round(payment, 2),
                    "is_paid": False,
                    "bill_id": bill_id,
                })
                debt_remaining -= payment
                creditors[creditor] -= payment
                if debt_remaining <= 0:
                    break
        
        for entry in ledgers:
            ledger_ref = Ledgers()
            ledger_ref.create(entry)

        return Ledgers.get_ledgers_by_bill(bill_id)

    def get_bill(self, bill_id):
        bill = Bill(bill_id)
        data = bill.get()

        if not data:
            raise CustomError("bill not found", 404)

        if data.get('is_finalized', True) is False:
            raise CustomError("bill is a draft", 403)
        
        payments = bill.get_payments()
        participants = bill.get_participants()
        items = bill.get_items()
        for i in items:
            i['assignments'] = Items(bill_id=bill.id, id=i['item_id']).get_assignments()

        resp = {
            **data,
            'payments': payments,
            'ledgers': participants,
            'items': items
        }

        return resp
    
    def get_draft_bill(self, bill_id):
        bill = Bill(bill_id)
        data = bill.get()

        if not data:
            raise CustomError("bill not found", 404)

        if data.get('is_finalized', True) is True:
            raise CustomError("bill is finalized", 403)
        
        payments = bill.get_payments()
        participants = bill.get_participants()
        items = bill.get_items()
        for i in items:
            i['assignments'] = Items(bill_id=bill.id, id=i['item_id']).get_assignments()

        resp = {
            **data,
            'payments': payments,
            'ledgers': participants,
            'items': items
        }

        return resp
    
    def get_all_bill(self, user_id):
        bills = Bill.get_all(user_id)
        resp = []
        for data in bills:
            payments = Bill(data['id']).get_payments()
            participants = Bill(data['id']).get_participants()
            
            users = []
            for person in data['participants']:
                user = User(person).get()
                users.append(user)

            total_credit = 0
            for pay in payments:
                if pay['paid_by'] == user_id:
                    total_credit = pay['amount']
                    break
            
            total_debt = 0
            for p in participants:
                if p['participant_id'] == user_id:
                    total_debt = p['amount_owed']
                    break

            resp.append({
                'bill_name': data['bill_name'],
                'total_price': data.get('total_price', 0),
                'total_debt': total_debt,
                'total_credit': total_credit,
                'created_at': data.get('created_at', '1999-01-01T00:00:00Z'),
                'participants': users
            })

        return resp

    def join_bill(self, bill_id, user_id=None):
        ref = Bill(bill_id)
        data = ref.get()

        if not data:
            raise CustomError("bill not found", 404)
        
        if data.get('is_finalized', False):
            raise CustomError("bill is finalized", 403)
        
        group_id = data.get('group_id', None)

        if group_id is not None:
            raise CustomError("bill is part of a group, cannot join individually", 403)

        participants = data.get('participants', [])

        join_user_id = user_id or ctx.user_id

        if join_user_id in participants:
            raise CustomError("user already joined the bill", 400)

        participants.append(join_user_id)

        ref.update({'participants': participants})

        data['participants'] = participants

        return data
    
    def assign_group(self, bill_id, group_id):
        ref = Bill(bill_id)
        data = ref.get()

        if not data:
            raise CustomError("bill not found", 404)
        
        if data.get('is_finalized', False):
            raise CustomError("bill is finalized", 403)
        
        group_ref = Groups(group_id)
        group_data = group_ref.get()

        if not group_data:
            raise CustomError("group not found", 404)

        ref.update({'group_id': group_id})

        return ref.get()

    def assign_items(self, bill_id, item_id, assignments):
        bill = Bill(bill_id)
        item = Items(bill_id=bill_id, id=item_id)

        if not bill.get():
            raise CustomError("bill not found", 404)
        
        if not item.get():
            raise CustomError("item not found", 404)

        for assignment in assignments:
            user_id = assignment.get('user_id')
            quantity = assignment.get('quantity', 1)

            if not user_id:
                raise CustomError("user_id is required for assignment", 400)

            assignment_ref = Assignments.create_ref(
                bill_id=bill.id,
                item_id=item.id,
                user_id=user_id
            )

            assignment_ref.set({
                'user_id': user_id,
                'quantity': quantity,
            })

        return item.get_assignments()
    
    def assign_payments(self, bill_id, payments):
        bill = Bill(bill_id)

        if not bill.get():
            raise CustomError("bill not found", 404)
        
        for payment in payments:
            amount = payment.get('amount')
            paid_by = payment.get('paid_by', ctx.user_id)

            if not amount:
                raise CustomError("amount is required for payment", 400)

            payment_ref = Payments.create_ref(bill_id=bill.id)
            payment_ref.create({
                'amount': amount,
                'paid_by': paid_by,
            })

        return bill.get_payments()
    
    def finalize_bill(self, bill_id, args):
        bill = Bill(bill_id)

        if not bill.get():
            raise CustomError("bill not found", 404)
        
        if bill.get().get('is_finalized', False):
            raise CustomError("bill is already finalized", 403)
        
        if args.get('bill_name'):
            bill.update({'bill_name': args['bill_name']})
        

        self.create_participant(bill_id=bill.id)

        self.create_ledgers(bill_id=bill.id)

        data = bill.get()

        payments = bill.get_payments()
        participants = bill.get_participants()
        items = bill.get_items()
        for i in items:
            i['assignments'] = Items(bill_id=bill.id, id=i['item_id']).get_assignments()

        resp = {
            **data,
            'payments': payments,
            'ledgers': participants,
            'items': items
        }
        
        bill.update({'is_finalized': True})

        return resp

    def create_participant(self, bill_id):
        bill = Bill(bill_id)

        if not bill.get():
            raise CustomError("bill not found", 404)
        
        if bill.get().get('is_finalized', False):
            raise CustomError("bill is finalized", 403)
        
        items = bill.get_items()

        if not items:
            raise CustomError("no items in the bill", 400)
        
        payments = bill.get_payments()

        if not payments:
            raise CustomError("no payments in the bill", 400)
        
        total_per_participant = {}
        
        for item in items:
            item['assignments'] = Items(bill_id=bill.id, id=item['item_id']).get_assignments()

            if not item.get('assignments'):
                raise CustomError("item assignments are required", 400)
            
            for assignment in item['assignments']:
                user_id = assignment.get('user_id')
                quantity = assignment.get('quantity', 1)

                if not user_id:
                    raise CustomError("user_id is required for assignment", 400)

                total_per_participant[user_id] = total_per_participant.get(user_id, 0) + (item['unit_price'] * quantity)

        for payment in payments:
            paid_by = payment.get('paid_by', ctx.user_id)
            amount = payment.get('amount', 0)

            if not paid_by:
                raise CustomError("paid_by is required for payment", 400)

            total_per_participant[paid_by] = total_per_participant.get(paid_by, 0) - amount

            if total_per_participant[paid_by] <= 0:
                total_per_participant.pop(paid_by, None)

        participants = []
        for user_id, amount in total_per_participant.items():
            participant_ref = Participants.create_ref(bill_id=bill.id, participant_id=user_id)
            participant_ref.create({
                'amount_owed': amount,
                'is_settled': False,
            })
            participant_dict = participant_ref.get().to_dict()
            participant_dict['participant_id'] = participant_ref.id

            participants.append(participant_dict)

        return participants