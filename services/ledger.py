from datetime import datetime
from models import Bill, Groups, Items, Assignments, Participants, Payments, Ledgers
from utils.error import CustomError
from flask import g as ctx
from utils.clean import clean_datetime

class LedgerService:
  def get_total_ledger(self, user_id):
    debt_ledgers = Ledgers.get_all_debt(user_id)
    credit_ledgers = Ledgers.get_all_credit(user_id)

    total_debt = 0
    for debt in debt_ledgers:
      total_debt += debt['amount']

    total_credit = 0
    for credit in credit_ledgers:
      total_credit += credit['amount']

    resp = {
      'total_debt': total_debt,
      'total_credit': total_credit
    }

    return resp
  
  def get_all_ledger(self, user_id):
    debt_ledgers = Ledgers.get_all_debt(user_id)
    credit_ledgers = Ledgers.get_all_credit(user_id)

    resp = {
      'debt': debt_ledgers,
      'credit': credit_ledgers
    }

    return resp
  
  def settle_debt(self, ledger_id, user_id):
    ledger = Ledgers(ledger_id)

    data = ledger.get()

    if(data['creditorUserId'] != user_id):
      raise CustomError('only creditor allowed to settle debt', 403)
    
    data_on_bill = Participants(data['bill_id'], data['debtorUserId'])

    if data_on_bill is None:
      raise CustomError('bill is not found', 404)

    amount_paid = data_on_bill.get('amountPaid', 0)
    amount_owed = data_on_bill.get('amountOwed', 0)

    amount_paid += data['amount']

    if amount_owed == amount_paid:
      data_on_bill['isSettled'] = True

    Participants(data['bill_id'], data['debtorUserId']).update(data_on_bill)

    data['isPaid'] = True
    Ledgers(ledger_id).update(data)

    return data

    
    
    
    