from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import hashlib
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("registration-64a55-firebase-adminsdk-fbsvc-e0be139804.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask("Reg")

current_user = None

class User:
    def __init__(self, email, password):
        self.password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self.email = email
    

class UserData(User):
    def __init__(self, data):
        self.data = data
        super().__init__(data["email"], data["password"])
        self.data["password"] = self.password
        self.data["isAdmin"] = False

    def post(self):
        db.collection("users").document(self.email).set(self.data)
        


@app.route("/", methods=["POST", "GET"])
def main():
    return render_template("index.html", form_open=False)

@app.route("/register", methods=["POST"])
def register():
    form_data = request.form.to_dict()
    user = UserData(form_data)
    user.post()
    return redirect(url_for("main"))

@app.route("/enter", methods=["POST"])
def enter():
    form_data = request.get_json()

    current_user = User(form_data["email"], form_data["password"])
    user_data = db.collection("users").document(current_user.email).get()
    
    if not user_data.exists:
        current_user = None
        return jsonify({"exists": user_data.exists}) 
    else:
        return jsonify({"exists": user_data.exists}) 
    


if __name__ == "__main__":
    app.run()
