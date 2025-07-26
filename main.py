from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from back.section import Section
from back.user import User, UserData
from back.create_table import import_data_to_file
from database.init_db import db
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt,get_jwt_identity,unset_jwt_cookies,jwt_required, JWTManager, current_user
from datetime import timedelta
import hashlib

app = Flask("Reg")
app.secret_key = "secret_key"
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

app.config["JWT_SECRET_KEY"] = "SECRET-KEY"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)



@jwt.user_identity_loader
def user_identity_loader(user):
    return user.email

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.collection("users").document(identity)

@app.route("/api/account")
@jwt_required()
def account():
    # Получаем данные пользователя из Firestore
    user_dict = current_user.get().to_dict() or {}

    return jsonify({
        "user":user_dict,
        })

@app.route("/api/games")
def games():
    
    games = db.collection("section").stream()

    data = []
    for game in games:
        game = game.to_dict()
        
        users = []
        users_ref = db.collection("users").where("sections", "array_contains", game["name"]).stream()
        for user in users_ref:
            users.append(user.get("name"))
        game["users"] = users
        data.append("game")

    return jsonify(data)

@app.route('/api/update-user', methods=['POST'])
@jwt_required()
def update_user():
    user_ref = current_user
    updates = {}
    data = request.form

    updates['name'] = data.get('name')
    updates['email'] = data.get('email')
    if data.get('password'):
        updates['password'] = hashlib.sha256(data.get('password').encode("utf-8")).hexdigest()
        user_ref.update(updates)
    else:
        user_ref.update(updates)
        updates['password']= None

    doc = user_ref.get().to_dict()
    db.collection("users").document(updates['email']).set(doc)

    user_ref.delete()

    user = User(
            updates["email"],
            doc.get("password"),
            is_admin=doc.get("isAdmin", False)
        )

    unset_jwt_cookies()
    token = create_access_token(identity=user)
    return jsonify({"token": token})





@app.route("/api/register", methods=["POST"])
def register():
    form_data = request.get_json()
    email = form_data.get("email")
    password = form_data.get("password")
    name = form_data.get("name")
    contact = form_data.get("contact")
    image = ""

    user_ref = db.collection("users").document(email)
    user_data = user_ref.get()

    if user_data.exists:
        return jsonify({"exists": True, "token": ""})

    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    user_info = {
        "email": email,
        "password": password_hash,
        "name": name,
        "contact": contact,
        "image": image,
        "isAdmin": False,
        "sections": []
    }
    user_ref.set(user_info)
    user_data = user_ref.get()

    user = User(
            user_data.get("email"),
            user_data.get("password"),
            user_data.get("isAdmin")
            )
    token = create_access_token(identity=user)

    return jsonify({"exists": False, "token": token})


@app.route("/api/enter", methods=["POST"])
def enter():
    form_data = request.get_json()
    user_data = db.collection("users").document(form_data["email"]).get()
    user_dict = user_data.to_dict()

    password_hash = hashlib.sha256(form_data["password"].encode("utf-8")).hexdigest()

    is_exist = user_data.exists 
    is_pass_match = user_data.get("password") == password_hash

    respond = {"exists": user_data.exists, "passMatch": is_pass_match, "token":None}

    if not is_exist or not is_pass_match:
        return jsonify(respond)
    else:
        user = User(
            form_data["email"],
            user_dict.get("password"),
            is_admin=user_dict.get('isAdmin', False)
        )

        token = create_access_token(identity=user)
        respond["token"] = token
        return jsonify(respond)


@app.route("/api/createSection", methods=["POST"])
def createSection():

    user_data = current_user.get().to_dict()
    if user_data["isAdmin"] == False:
        return "Доступ запрещён", 403
    else:
        form_data = request.form.to_dict()

        current_section = Section(form_data)

        if not current_section.isExist():
            current_section.post()
        else:
            current_section.update(form_data)

    return "ok"

@app.route("/api/entryToSection", methods=["POST"])
@jwt_required()
def entryToSection():
    form_data = request.get_json()

    forUser, forSection = {}, {}

    usersFrSection = db.collection('section').document(form_data['id']).get().to_dict()
    sectionsFrUser = current_user.get().to_dict()

    if int(usersFrSection['counter']) > 0:
        if form_data['id'] not in sectionsFrUser['sections']:
            sectionsFrUser['sections'].append(form_data['id'])

            forUser['sections'] = sectionsFrUser['sections']
            forSection['counter'] = str(int(usersFrSection['counter']) - 1)

            db.collection('section').document(form_data['id']).set(forSection, merge=True)
            current_user.set(forUser, merge=True)

    return "ok"

@app.route('/api/delete-entry/<entry_id>', methods=['POST'])
def delete_entry(entry_id):
    section_ref = db.collection("section").document(entry_id).get()
    section = section_ref.to_dict()
    
    section["counter"] = str(int(section["counter"]) + 1)

    db.collection("section").document(entry_id).set(section)

    user_ref = current_user.get()
    user = user_ref.to_dict()

    ind = user["sections"].index(entry_id)
    user["sections"].pop(ind)

    db.collection("users").document(email).set(user)

    return "ok"

@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route("/api/download")
def download():
    import_data_to_file()
    return send_file("static/files/registredUsers.xlsx", as_attachment=True)


if __name__ == "__main__":
    app.run()



