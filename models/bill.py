from firebase.config import db

class Bill:
    def __init__(self, uid=None):
        """
        If uid is provided, points to that user document.
        If uid is None, instance won't be tied to a specific document (use create_user instead).
        """
        self.uid = uid
        self.ref = db.collection("bills").document(uid) if uid else None

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
        return doc.to_dict() if doc.exists else None

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

    def create_bill(self, data):
        """
        Create a new bill document with an auto-generated uid and return its data.
        """
        new_ref = db.collection("bills").document()

        return new_ref