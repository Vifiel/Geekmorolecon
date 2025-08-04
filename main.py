import json

from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt,get_jwt_identity,unset_jwt_cookies,jwt_required, JWTManager, current_user

from back.section import Section
from back.user import User, UserData
from back.create_table import import_data_to_file

from database.init_db import db

from datetime import timedelta, datetime, timezone

import hashlib

import base64


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
    user_snapshot = db.collection("users").document(identity)
    return user_snapshot if user_snapshot.get().exists else None

@app.route("/api/account")
@jwt_required()
def account():
    # Получаем данные пользователя из Firestore
    print(response.get_json())
    user_dict = current_user.get().to_dict() or {}

    return jsonify({
        "user":user_dict,
        })

@app.route("/api/games")
def games():
    
    games = db.collection("section").stream()

    data = []
    for game in games:
        game_id = game.id
        game = game.to_dict()
        game["id"] = game_id
        data.append(game)

    return jsonify(data)


@app.route("/api/games/<game_id>")
def game_by_id(game_id):
    game_ref = db.collection("section").document(game_id).get()

    if not game_ref.exists:
        return jsonify({"error": "Game not found"}), 500

    game = game_ref.to_dict()
    game["id"] = game_id

    users = []
    users_ref = db.collection("users").where("sections", "array_contains", game["id"]).stream()
    for user in users_ref:
        users.append(user.get("name"))

    game["users"] = users

    return jsonify(game)

@app.route("/api/user-games")
@jwt_required()
def user_games():
    ids = current_user.get().to_dict()["sections"]
    print(ids)
    
    data = []
    for game_id in ids:
        game = db.collection("section").document(game_id).get().to_dict()
        game["id"] = game_id

        data.append(game)

    return jsonify(data)


@app.route('/api/update-user', methods=['POST'])
@jwt_required()
def update_user():
    data = request.get_json()
    token = request.headers.get("Authorization", "").replace("Bearer ", "")

    email = data.pop("email", None)
    if email:
        doc = current_user.get().to_dict()
        doc["email"] = email
        print(doc)
        db.collection("users").document(email).set(doc)
        user_data = db.collection("users").document(email).get().to_dict()

        current_user.delete()
        unset_jwt_cookies(jsonify({"msg": "change"}))
        
        user = User(
                email = user_data["email"],
                password = user_data["password"],
                is_admin = user_data["isAdmin"])

        token = create_access_token(identity=user)
        return jsonify(token)

    else:
        current_user.update(data)

        return jsonify(token)


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
    print(token)

    return jsonify({"exists": False, "token": token})


@app.route("/api/enter", methods=["POST"])
def enter():
    form_data = request.get_json()
    user_data = db.collection("users").document(form_data["email"]).get()
    user_dict = user_data.to_dict()

    password_hash = hashlib.sha256(form_data["password"].encode("utf-8")).hexdigest()

    is_exist = user_data.exists 
    is_pass_match = user_data.get("password") == password_hash

    respond = {"exists": user_data.exists, "passMatch": is_pass_match, "token":""}
    print(respond)

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
        print(token)
        return jsonify(respond)


@app.route("/api/createSection", methods=["POST"])
@jwt_required()
def createSection():

    user_data = current_user.get().to_dict()
    if user_data["isAdmin"] == False:
        return "Доступ запрещён", 403
    else:
        form_data = request.form.to_dict()
        current_section = Section(form_data)

        if "image" in request.files:
            image = request.files["image"]
            image.save(f"static/images/games/{current_secton.id}.jpg")
        else:
            current_section.image = "http://localhost:5000/static/images/games/blank.png"

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

            db.collection('section').document(form_data['id']).update(forSection)
            current_user.update(forUser)

    return "ok"

@app.route('/api/delete-entry/<entry_id>', methods=['POST'])
@jwt_required()
def delete_entry(entry_id):
    user = current_user.get().to_dict()
    
    if entry_id in user["sections"]:
        ind = user["sections"].index(entry_id)
        user["sections"].pop(ind)

        current_user.set(user)
        section_ref = db.collection("section").document(entry_id).get()
        section = section_ref.to_dict()
        
        section["counter"] = str(int(section["counter"]) + 1)

        db.collection("section").document(entry_id).set(section)

        return jsonify("ok")

    else:
        return jsonify("Not signed")

@app.route('/api/delete-entry/<section_id>/<user_id>')
@jwt_required()
def admin_delete_entry(section_id, user_id):

    if current_user.get().get("isAdmin") == False:
        return "Доступ запрещён", 403
    else:
        section_ref = db.collection("section").document(section_id).get()
        section = section_ref.to_dict()
        
        section["counter"] = str(int(section["counter"]) + 1)

        db.collection("section").document(section_id).update(section)

        user_ref = db.collection("users").document(user_id)
        user = user_ref.get().to_dict()

        ind = user["sections"].index(section_id)
        user["sections"].pop(ind)

        user_ref.update(user)

        return "ok"


@app.route('/api/update-section/<section_id>')
@jwt_required()
def updateSection(section_id):
    if current_user.get("isAdmin") == False:
        return "Доступ запрещён", 403
    else:
        update_data = request.get_json()
        db.collection('section').document(section_id).update(update_data)

        return "ok"
    
@app.route("/api/logout")
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



