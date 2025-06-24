import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("registration-64a55-firebase-adminsdk-fbsvc-e0be139804.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
