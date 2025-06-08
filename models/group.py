from firebase.config import db
from uuid import uuid4
from datetime import datetime

class Groups:
    def __init__(self, id=None):
        """
        If id is provided, points to that group document.
        If id is None, instance will create a new group with an auto-generated id.
        """
        self.id = id or str(uuid4())
        self.ref = db.collection("groups").document(self.id)

    def get(self):
        if not self.ref:
            raise ValueError("Group id is not set.")
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
            raise ValueError("Group id is not set.")
        self.ref.update(data)

    def delete(self):
        if not self.ref:
            raise ValueError("Group id is not set.")
        self.ref.delete()
