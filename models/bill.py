from firebase.config import db
from uuid import uuid4
from datetime import datetime

class Bill:
    def __init__(self, id=None):
        """
        If id is provided, points to that user document.
        If id is None, instance won't be tied to a specific document (use create_user instead).
        """
        self.id = id or str(uuid4())
        self.ref = db.collection("bills").document(self.id)

    def create(self, data):
        """
        Create or overwrite the user document at self.id.
        """
        self.ref.set({
            **data,
            "created_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        })
        return self.get()


    def get(self):
        """
        Get the user data dictionary for self.id.
        """
        if not self.ref:
            raise ValueError("User id is not set.")
        doc = self.ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = self.id
            return data
        return None
    
    def get_payments(self):
        """
        Get all payments associated with this bill, including their document IDs.
        """
        if not self.ref:
            raise ValueError("Bill id is not set.")
        payments_ref = self.ref.collection("payments")
        payments = [
            {**doc.to_dict(), "payment_id": doc.id} for doc in payments_ref.stream()
        ]
        return payments

    
    def get_items(self):
        """
        Get all items associated with this bill, including their document IDs.
        """
        if not self.ref:
            raise ValueError("Bill id is not set.")
        items_ref = self.ref.collection("items")
        items = [
            {**doc.to_dict(), "item_id": doc.id} for doc in items_ref.stream()
        ]
        return items

    
    def get_participants(self):
        """
        Get all participants associated with this bill, including their document IDs.
        """
        if not self.ref:
            raise ValueError("Bill id is not set.")
        participants_ref = self.ref.collection("participants")
        participants = [
            {**doc.to_dict(), "participant_id": doc.id} for doc in participants_ref.stream()
        ]
        return participants


    def update(self, data):
        """
        Update the user document at self.id.
        """
        if not self.ref:
            raise ValueError("User id is not set.")
        self.ref.update(data)

    def delete(self):
        """
        Delete the user document at self.id.
        """
        if not self.ref:
            raise ValueError("User id is not set.")
        self.ref.delete()

    @staticmethod
    def create_ref():
        """
        Create a new bill document with an auto-generated id and return its reference.
        """
        new_ref = db.collection("bills").document()
        return new_ref
    
    @staticmethod
    def get_all(user_id):
        """
        Get all bills that include this user either directly or through group membership.
        """
        bills_ref = db.collection("bills")
        group_ref = db.collection("groups")

        # 1. Get all groups where the user is a member
        user_groups = []
        groups = group_ref.where("members", "array_contains", user_id).stream()
        for group in groups:
            user_groups.append(group.id)

        # 2. Get all bills where:
        #   - the user is directly a participant (no group_id)
        #   - OR the bill's group_id is in user_groups
        bills = bills_ref.stream()
        result = []

        for bill in bills:
            data = bill.to_dict()
            data["id"] = bill.id

            if (
                data.get("group_id") in user_groups
                or user_id in data.get("participants", [])
            ):
                result.append(data)

        return result