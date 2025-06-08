from firebase.config import db
from uuid import uuid4
from datetime import datetime

class Ledgers:
    def __init__(self, id=None):
        """
        If uid is provided, points to that ledgers document.
        If uid is None, instance will create a new ledgers with an auto-generated uid.
        """
        self.id = id or str(uuid4())
        self.ref = db.collection("ledgers").document(self.id)

    def get(self):
        if not self.ref:
            raise ValueError("ledgers uid is not set.")
        doc = self.ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = self.id
            return data
        return None
    
    def get_ledgers_by_bill(bill_id: str):
        query = db.collection("ledgers").where("bill_id", "==", bill_id)
        docs = query.stream()
        return [doc.to_dict() | {"id": doc.id} for doc in docs]

    def create(self, data):
        self.ref.set({
            **data,
            "created_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        })
        return self.get()


    def update(self, data):
        if not self.ref:
            raise ValueError("ledgers uid is not set.")
        self.ref.update(data)

    def delete(self):
        if not self.ref:
            raise ValueError("ledgers uid is not set.")
        self.ref.delete()

    @staticmethod
    def get_all_debt(user_id):
        query = db.collection("ledgers").where("debtor_user_id", "==", user_id)
        docs = query.stream()
        return [doc.to_dict() | {"id": doc.id} for doc in docs]
    
    @staticmethod
    def get_all_credit(user_id):
        query = db.collection("ledgers").where("creditor_user_id", "==", user_id)
        docs = query.stream()
        return [doc.to_dict() | {"id": doc.id} for doc in docs]
    
    @staticmethod
    def get_all_unpaid_debt(user_id):
        query = db.collection("ledgers").where("debtor_user_id", "==", user_id).where("is_paid", "==", False)
        docs = query.stream()
        return [doc.to_dict() | {"id": doc.id} for doc in docs]
    
    @staticmethod
    def get_all_unpaid_credit(user_id):
        query = db.collection("ledgers").where("creditor_user_id", "==", user_id).where("is_paid", "==", False)
        docs = query.stream()
        return [doc.to_dict() | {"id": doc.id} for doc in docs]
