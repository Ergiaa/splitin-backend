from datetime import datetime
from models import Bill, Groups, Items, Assignments, Participants, Payments, Ledgers, User
from utils.error import CustomError
from flask import g as ctx
from utils.clean import clean_datetime

class LedgerService:
    def get_total_ledger(self, user_id):
        debt_ledgers = Ledgers.get_all_unpaid_debt(user_id)
        credit_ledgers = Ledgers.get_all_unpaid_credit(user_id)

        total_debt = 0
        for debt in debt_ledgers:
            total_debt += debt['amount']

        total_credit = 0
        for credit in credit_ledgers:
            total_credit += credit['amount']

        resp = {
            'total_debt': total_debt,
            'total_credit': total_credit,
        }

        return resp
    
    def get_all_ledger(self, user_id, page=1, limit=10):
        debt_ledgers = Ledgers.get_all_debt(user_id)
        credit_ledgers = Ledgers.get_all_credit(user_id)

        user_ids = set()
        bill_ids = set()
        for ledger in debt_ledgers + credit_ledgers:
            user_ids.add(ledger['debtor_user_id'])
            user_ids.add(ledger['creditor_user_id'])
            bill_ids.add(ledger['bill_id'])

        users = User.get_by_ids(list(user_ids))

        # Fetch bills and create a lookup dictionary
        bills = {}
        for bill_id in bill_ids:
            bill_data = Bill(bill_id).get()  # Assuming .get() returns a dict with at least `bill_name`
            if bill_data:
                bills[bill_id] = bill_data

        def get_user_data(user_id):
            user_data = users.get(user_id)
            return {
                "id": user_id,
                "username": user_data.get("username", "") if user_data else "",
                "email": user_data.get("email", "") if user_data else "",
                "phone_number": user_data.get("phone_number", "") if user_data else ""
            }

        def get_bill_name(bill_id):
            return bills.get(bill_id, {}).get("bill_name", "")

        data = []

        for debt in debt_ledgers:
            data.append({
                **debt,
                'ledger_type': 'debt',
                'bill_name': get_bill_name(debt['bill_id']),
                'debtor_user': get_user_data(debt['debtor_user_id']),
                'creditor_user': get_user_data(debt['creditor_user_id']),
            })

        for credit in credit_ledgers:
            data.append({
                **credit,
                'ledger_type': 'credit',
                'bill_name': get_bill_name(credit['bill_id']),
                'debtor_user': get_user_data(credit['debtor_user_id']),
                'creditor_user': get_user_data(credit['creditor_user_id']),
            })

        data.sort(key=lambda x: x['created_at'])

        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_data = data[start:end]

        return paginated_data

    
    def settle_debt(self, ledger_id, user_id):
        ledger = Ledgers(ledger_id)
        data = ledger.get()

        if data['creditor_user_id'] != user_id:
            raise CustomError('only creditor allowed to settle debt', 403)
        
        data_on_bill = Participants(bill_id=data['bill_id'], id=data['debtor_user_id']).get()

        if data_on_bill is None:
            raise CustomError('bill is not found', 404)
        
        if data.get('is_paid', True):
            raise CustomError('ledger is already settled', 403)

        amount_paid = data_on_bill.get('amount_paid', 0)
        amount_owed = data_on_bill.get('amount_owed', 0)

        amount_paid += data['amount']

        data_on_bill['amount_paid'] = amount_paid
        data_on_bill['amount_owed'] = amount_owed

        if amount_owed == amount_paid:
            data_on_bill['is_settled'] = True

        print(data_on_bill)
        Participants(bill_id=data['bill_id'], id=data['debtor_user_id']).update(data_on_bill)

        data['is_paid'] = True
        Ledgers(ledger_id).update(data)

        return data
