import firebase_admin
from firebase_admin import firestore
import os

firebase_key = os.getenv("FIREBASE_KEY")
cred = firebase_admin.credentials.Certificate(firebase_key)
firebase_admin.initialize_app(cred)

db = firestore.client()
