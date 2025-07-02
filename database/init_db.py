import firebase_admin
from firebase_admin import firestore
import os
import tempfile
from dotenv import load_dotenv

firebase_key = os.getenv("FIREBASE_KEY")

if firebase_key:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
        temp.write(firebase_key.encode())
        temp_path = temp.name
        key = temp_path
    cred = firebase_admin.credentials.Certificate(temp_path)
    firebase_admin.initialize_app(cred)

    os.remove(temp_path)
else:
    key = "registration-64a55-firebase-adminsdk-fbsvc-1cd4355a96.json"

    cred = firebase_admin.credentials.Certificate(key)
    firebase_admin.initialize_app(cred)

db = firestore.client()
