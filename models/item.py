from firebase.config import db
from google.cloud import firestore  # Add this import
from uuid import uuid4
from datetime import datetime

class Items:
    def __init__(self,bill_id,id=None):
        """
        If id is provided, points to that item document.
        If id is None, instance will create a new item with an auto-generated id.
        """
        self.bill_id = bill_id
        self.id = id or str(uuid4())
        self.ref = db.collection("bills").document(bill_id).collection("items").document(self.id)

    def get(self):
        if not self.ref:
            raise ValueError("item id is not set.")
        doc = self.ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = self.id
            return data
        return None
    
    def get_assignments(self):
        if not self.ref:
            raise ValueError("item id is not set.")
        assignments_ref = self.ref.collection("assignments")
        assignments = [doc.to_dict() for doc in assignments_ref.stream()]
        return assignments

    def create(self, data):
        self.ref.set({
            **data,
        })
        return self.get()

    def update(self, data):
        if not self.ref:
            raise ValueError("item id is not set.")
        self.ref.update(data)

    def delete(self):
        if not self.ref:
            raise ValueError("item id is not set.")
        self.ref.delete()

    @staticmethod
    def create_ref(bill_id):
        """
        Create a new item document with an auto-generated id and return its reference.
        """
        bill_ref = db.collection("bills").document(bill_id)
        new_ref:firestore.DocumentReference = bill_ref.collection("items").document()
        return new_ref