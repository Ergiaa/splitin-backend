from firebase.config import db
from uuid import uuid4

class User:
    def __init__(self, id=None):
        """
        If uid is provided, points to that user document.
        If uid is None, instance won't be tied to a specific document (use create_user instead).
        """
        self.id = id or str(uuid4())
        self.ref = db.collection("users").document(self.id)

    def create(self, data):
        """
        Create or overwrite the user document at self.id.
        """
        if not self.ref:
            raise ValueError("User id is not set. Use create_user() for new users.")
        self.ref.set(data)

    def get(self):
        """
        Get the user data dictionary for self.id.
        """
        if not self.ref:
            raise ValueError("User id is not set.")
        doc = self.ref.get()
        if doc.exists:
            data = doc.to_dict()
            data.pop('password')
            data["id"] = self.id  # Include id in the returned data
            return data
        return None

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
    def create_user(data):
        """
        Create a new user document with an auto-generated id and return its data.
        """
        new_ref = db.collection("users").document()  # auto-generated ID
        new_ref.set(data)
        return {"id": new_ref.id, **new_ref.get().to_dict()}

    @staticmethod
    def exists(data):
        """
        Check if a user exists by email or username.
        Returns dictionary indicating existence and matched fields.
        """
        email_query = db.collection("users")\
                        .where("email", "==", data.get("email"))\
                        .limit(1)
        username_query = db.collection("users")\
                        .where("username", "==", data.get("username"))\
                        .limit(1)

        email_results = email_query.get()
        username_results = username_query.get()

        user_email = email_results[0].to_dict() if email_results else None
        user_username = username_results[0].to_dict() if username_results else None

        if user_email or user_username:
            return {
                "exists": True,
                "by_email": bool(user_email),
                "by_username": bool(user_username),
                "user_email": user_email,
                "user_username": user_username
            }

        return {"exists": False}

    @staticmethod
    def get_by_ids(user_ids):
        """
        Fetch multiple users from Firestore by document ID.
        Returns a dictionary mapping user_id -> user_data.
        """
        result = {}
        users_ref = db.collection("users")

        for user_id in user_ids:
            doc_ref = users_ref.document(user_id)
            doc = doc_ref.get()
            if doc.exists:
                result[user_id] = doc.to_dict()

        return result