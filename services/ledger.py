from datetime import datetime
from models import Bill, Groups, Items, Assignments, Participants, Payments, Ledgers
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
    
    def get_all_ledger(self, user_id):
        debt_ledgers = Ledgers.get_all_debt(user_id)
        credit_ledgers = Ledgers.get_all_credit(user_id)

        data = []

        for debt in debt_ledgers:
            data.append({
                **debt,
                'ledger_type': 'debt'
            })

        for credit in credit_ledgers:
            data.append({
                **credit,
                'ledger_type': 'credit'
            })

        data.sort(key=lambda x: x['created_at'])

        return data
    
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
