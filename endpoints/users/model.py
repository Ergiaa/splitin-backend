from firebase.config import db

class User:
    def __init__(self, uid=None):
        """
        If uid is provided, points to that user document.
        If uid is None, instance won't be tied to a specific document (use create_user instead).
        """
        self.uid = uid
        self.ref = db.collection("users").document(uid) if uid else None

    def create(self, data):
        """
        Create or overwrite the user document at self.uid.
        """
        if not self.ref:
            raise ValueError("User uid is not set. Use create_user() for new users.")
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

    @staticmethod
    def create_user(data):
        """
        Create a new user document with an auto-generated uid and return its data.
        """
        new_ref = db.collection("users").document()  # auto-generated ID
        new_ref.set(data)
        return {"uid": new_ref.id, **new_ref.get().to_dict()}

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
