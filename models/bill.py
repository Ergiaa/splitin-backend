from firebase.config import db
from uuid import uuid4

class Bill:
    def __init__(self, uid=None):
        """
        If uid is provided, points to that user document.
        If uid is None, instance won't be tied to a specific document (use create_user instead).
        """
        self.uid = uid or str(uuid4())
        self.ref = db.collection("bills").document(self.uid)

    def create(self, data):
        """
        Create or overwrite the user document at self.uid.
        """
        if not self.ref:
            raise ValueError("Bill uid is not set. Use create_bill() for new bill.")
        self.ref.set(data)

    def get(self):
        """
        Get the user data dictionary for self.uid.
        """
        if not self.ref:
            raise ValueError("User uid is not set.")
        doc = self.ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = self.uid
            return data
        return None
    
    def get_payments(self):
        """
        Get all payments associated with this bill.
        """
        if not self.ref:
            raise ValueError("Bill uid is not set.")
        payments_ref = self.ref.collection("payments")
        payments = [doc.to_dict() for doc in payments_ref.stream()]
        return payments
    
    def get_items(self):
        """
        Get all items associated with this bill.
        """
        if not self.ref:
            raise ValueError("Bill uid is not set.")
        items_ref = self.ref.collection("items")
        items = [doc.to_dict() for doc in items_ref.stream()]
        return items
    
    def get_participants(self):
        """
        Get all participants associated with this bill, including their document IDs.
        """
        if not self.ref:
            raise ValueError("Bill uid is not set.")
        participants_ref = self.ref.collection("participants")
        participants = [
            {**doc.to_dict(), "participant_id": doc.id} for doc in participants_ref.stream()
        ]
        return participants


    def update(self, data):
        """
        Update the user document at self.uid.
        """
        if not self.ref:
            raise ValueError("User uid is not set.")
        self.ref.update(data)

    def delete(self):
        """
        Delete the user document at self.uid.
        """
        if not self.ref:
            raise ValueError("User uid is not set.")
        self.ref.delete()

    @staticmethod
    def create_ref():
        """
        Create a new bill document with an auto-generated uid and return its reference.
        """
        new_ref = db.collection("bills").document()
        return new_ref