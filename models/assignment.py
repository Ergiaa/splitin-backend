from firebase.config import db
from google.cloud import firestore  # Add this import
from datetime import datetime

class Assignments:
    def __init__(self, bill_id, item_id, user_id):
        self.bill_id = bill_id
        self.item_id = item_id
        self.user_id = user_id
        self.ref = db.collection("bills")\
                     .document(bill_id)\
                     .collection("items")\
                     .document(item_id)\
                     .collection("assignments")\
                     .document(user_id)

    def get(self):
        doc = self.ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["user_id"] = self.user_id
            return data
        return None

    def create(self, data):
        self.ref.set({
            **data,
        })
        return self.get()

    def update(self, data):
        self.ref.update(data)

    def delete(self):
        self.ref.delete()

    @staticmethod
    def create_ref(bill_id, item_id, user_id):
        new_ref:firestore.DocumentReference = db.collection("bills")\
                     .document(bill_id)\
                     .collection("items")\
                     .document(item_id)\
                     .collection("assignments")\
                     .document(user_id)
        return new_ref