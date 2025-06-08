from firebase.config import db
from uuid import uuid4
from datetime import datetime

class Ledgers:
    def __init__(self, uid=None):
        """
        If uid is provided, points to that ledgers document.
        If uid is None, instance will create a new ledgers with an auto-generated uid.
        """
        self.uid = uid or str(uuid4())
        self.ref = db.collection("ledgers").document(self.uid)

    def get(self):
        if not self.ref:
            raise ValueError("ledgers uid is not set.")
        doc = self.ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = self.uid
            return data
        return None
    
    def get_ledgers_by_bill(bill_id: str):
        query = db.collection("ledgers").where("billId", "==", bill_id)
        docs = query.stream()
        return [doc.to_dict() | {"id": doc.id} for doc in docs]

    from datetime import datetime

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
        query = db.collection("ledgers").where("debtorUserId", "==", user_id).where("isPaid", "==", False)
        docs = query.stream()
        return [doc.to_dict() | {"id": doc.id} for doc in docs]
    
    @staticmethod
    def get_all_credit(user_id):
        query = db.collection("ledgers").where("creditorUserId", "==", user_id).where("isPaid", "==", False)
        docs = query.stream()
        return [doc.to_dict() | {"id": doc.id} for doc in docs]
