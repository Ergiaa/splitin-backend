from datetime import datetime
from models import Bill, Groups, Items, Assignments, Participants, Payments, Ledgers
from utils.error import CustomError
from flask import g as ctx
from utils.clean import clean_datetime
class BillService:
    def create_bill(self):
        ref = Bill.create_ref()

        participant = [ctx.user_id]

        data = {
            'bill_name': f'Split Bill-{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}-{ref.id}',
            'created_by': ctx.user_id,
            'join_code': ref.id,
            'participants': participant,
            'isFinalized': False,
        }

        ref.set(data)

        return ref.to_dict()
    
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

          participant = group_data.get('members', [])
          if ctx.user_id not in participant:
              participant.append(ctx.user_id)

        split_type = args.get('split_type', 'equal')
        
        bill_data = {
            'bill_name': f'Split Bill-{datetime.now().strftime("%Y-%m-%d-%H:%M:%S")}-{ref.id}',
            'created_by': ctx.user_id,
            'group_id': args.get('group_id', None),
            'join_code': ref.id,
            'participants': participant,
            'split_type': split_type,
            'isFinalized': True,
        }

        ref.set(bill_data)

        items = args.get('items', [])
        total_price = 0
        item_data = []
        for item in items:
            item_ref = Items.create_ref(bill_id=ref.id)

            item_data.append({
                'id': item_ref.id,
                'name': item.get('name'),
                'unitPrice': item.get('unitPrice'),
                'totalQuantity': item.get('totalQuantity', 1),
            })

            total_price += item.get('unitPrice', 0) * item.get('totalQuantity', 1)

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
                        'user_id':assignment.get('user_id'),
                        'quantity':assignment.get('quantity', 1),
                    })

        ref.update({
            'totalPrice': total_price,
        })

        if split_type == 'equal':
            # For equal split, assign total price to each participant
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
                assignment_ref = Items(bill_id=ref.id, uid=item['id']).get_assignments()

                for assignment in assignment_ref:
                    total_price = item['unitPrice'] * assignment['quantity']
                    if assignment['user_id'] not in participant_dict:
                        participant_dict[assignment['user_id']] = total_price
                    else:
                        participant_dict[assignment['user_id']] += total_price
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
        response['items'] = Bill(ref.id).get_items()
        for item in response['items']:
            item['assignments'] = Items(bill_id=ref.id, uid=item['id']).get_assignments()
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
        
        if participants is None or participants == []:
            raise CustomError("no participants in the bill", 400)
        
        if payments is None or payments == []:
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
                    "debtorUserId": debtor,
                    "creditorUserId": creditor,
                    "amount": round(payment, 2),
                    "isPaid": False,
                    "billId": bill_id,
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
        ref = Bill(bill_id)
        data = ref.get()

        if not data:
            raise CustomError("bill not found", 404)

        if data.get('isFinalized', False):
            raise CustomError("bill is finalized", 403)

        return data

    def join_bill(self, bill_id, user_id=None):
        ref = Bill(bill_id)
        data = ref.get()

        if not data:
            raise CustomError("bill not found", 404)
        
        if data.get('isFinalized', False):
            raise CustomError("bill is finalized", 403)

        participants = data.get('participants', [])

        # Use ctx.user_id if user_id param is None
        join_user_id = user_id or ctx.user_id

        if join_user_id in participants:
            raise CustomError("user already joined the bill", 400)

        participants.append(join_user_id)

        # Save the updated participants list back to DB
        ref.update({'participants': participants})

        # Return updated data after append
        data['participants'] = participants

        return data
