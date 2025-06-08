from firebase.config import db
from uuid import uuid4
from datetime import datetime

class Groups:
    def __init__(self, uid=None):
        """
        If uid is provided, points to that group document.
        If uid is None, instance will create a new group with an auto-generated uid.
        """
        self.uid = uid or str(uuid4())
        self.ref = db.collection("groups").document(self.uid)

    def get(self):
        if not self.ref:
            raise ValueError("Group uid is not set.")
        doc = self.ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = self.uid
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
            raise ValueError("Group uid is not set.")
        self.ref.update(data)

    def delete(self):
        if not self.ref:
            raise ValueError("Group uid is not set.")
        self.ref.delete()
