from flask import Flask, render_template, request, redirect, url_for, jsonify
from back.user import User, UserData
from back.section import Section
from database import init_db
import firebase_admin
from firebase_admin import credentials, firestore

#cred = credentials.Certificate("registration-64a55-firebase-adminsdk-fbsvc-e0be139804.json")
#firebase_admin.initialize_app(cred)

#db = firestore.client()

app = Flask("Reg")

current_user = None


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
    user_data = init_db.db.collection("users").document(current_user.email).get()
    is_exist = user_data.exists 
    is_pass_match = user_data.get("password") == current_user.password
    respond = jsonify({"exists": user_data.exists, "passMatch": is_pass_match})
    
    if not is_exist:
        current_user = None
        return  respond
    elif not is_pass_match:
        current_user = None
        return respond
    else:
        return respond

@app.route("/createSectionForm", methods=["POST"])
def createSection():
    form_data = request.form.to_dict()

    current_section = Section(form_data)
    current_section.post()

    return redirect(url_for("main"))

if __name__ == "__main__":
    app.run()
