import firebase_admin
from firebase_admin import firestore
import os
import tempfile

firebase_key = os.getenv("FIREBASE_KEY")

with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp:
    temp.write(firebase_creds_str.encode())
    temp_path = temp.name

cred = firebase_admin.credentials.Certificate(temp_path)
firebase_admin.initialize_app(cred)

os.remove(temp_path)

db = firestore.client()
