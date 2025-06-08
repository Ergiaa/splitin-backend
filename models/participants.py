from firebase.config import db
from google.cloud import firestore  # Add this import
from uuid import uuid4
from datetime import datetime

class Participants:
    def __init__(self, bill_id, id=None):
        self.bill_id = bill_id
        self.id = id
        self.ref = db.collection("bills").document(bill_id).collection("participants").document(id) if id else None

    def get(self):
        if not self.ref:
            raise ValueError("Participants uid is not set.")
        doc = self.ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = self.id
            return data
        return None

    def create(self, data):
        self.ref.set({
            **data,
        })
        return self.get()

    def update(self, data):
        if not self.ref:
            raise ValueError("Participants uid is not set.")
        self.ref.update(data)

    def delete(self):
        if not self.ref:
            raise ValueError("Participants uid is not set.")
        self.ref.delete()

    @staticmethod
    def create_ref(bill_id, participant_id):
        new_ref:firestore.DocumentReference = db.collection("bills")\
                     .document(bill_id)\
                     .collection("participants")\
                     .document(participant_id)
        return new_ref
