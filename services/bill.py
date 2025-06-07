from datetime import datetime
from models import Bill
from utils.error import CustomError
from flask import g as ctx

class BillService:
    def create_bill(self):
        ref = Bill.create_bill()

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
