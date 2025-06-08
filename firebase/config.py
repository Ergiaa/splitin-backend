import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore as admin_firestore
from google.cloud import firestore as gcloud_firestore
from settings import USE_FIRESTORE_EMULATOR, FIRESTORE_EMULATOR_HOST


def init_firebase():
    if USE_FIRESTORE_EMULATOR:
        # Set emulator env vars for google-cloud-firestore client
        os.environ["FIRESTORE_EMULATOR_HOST"] = FIRESTORE_EMULATOR_HOST
        os.environ["GOOGLE_CLOUD_PROJECT"] = "demo-project"
        # Return google-cloud-firestore client (not firebase_admin)
        return gcloud_firestore.Client()

    # For real Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase/key.json")
        firebase_admin.initialize_app(cred)
    return admin_firestore.client()


db = init_firebase()
