from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import hashlib
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("registration-64a55-firebase-adminsdk-fbsvc-e0be139804.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask("Reg")

class User:
    def __init__(self, email, password):
        self.password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self.email = email
    

class UserData(User):
    def __init__(self, data):
        super().__init__(data["email"], data["password"])
        self.data["password"] = self.password
        self.data["isAdmin"] = False

    def post(self):
        db.collection("users").document(self.email).set(self.data)
        


@app.route("/")
def main():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    form_data = request.form.to_dict()
    user = UserData(form_data)
    return redirect(url_for("main"))

if __name__ == "__main__":
    app.run()
