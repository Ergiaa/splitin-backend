from firebase.config import db
from google.cloud import firestore
from uuid import uuid4
from datetime import datetime

class Payments:
    def __init__(self, bill_id, payment_id=None):
        self.bill_id = bill_id
        self.payment_id = payment_id or str(uuid4())
        self.ref = db.collection("bills").document(bill_id).collection("payments").document(self.payment_id)

    def get(self):
        if not self.ref:
            raise ValueError("User uid is not set.")
        doc = self.ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = self.payment_id
            return data
        return None

    def create(self, data):
        self.ref.set({
            **data,
            "created_at": datetime.utcnow()
        })
        return self.get()

    def update(self, data):
        if not self.ref:
            raise ValueError("User uid is not set.")
        self.ref.update(data)

    def delete(self):
        if not self.ref:
            raise ValueError("User uid is not set.")
        self.ref.delete()

    @staticmethod
    def create_ref(bill_id):
        new_ref:firestore.DocumentReference = db.collection("bills")\
                     .document(bill_id)\
                     .collection("payments")\
                     .document()
        return new_ref