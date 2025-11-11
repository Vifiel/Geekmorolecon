import json

from flask import Flask, send_from_directory, render_template, request, redirect, url_for, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt,get_jwt_identity,unset_jwt_cookies,jwt_required, JWTManager, current_user

from back.mail_utils import generate_token, confirm_token, send_verification_email, mail

from back.section import Section
from back.user import User, UserData

from database.init_db import db

from datetime import timedelta, datetime, timezone

from random import randint

from app_config import app

import os

import hashlib

import base64




mail.init_app(app)

HOST = app.config["HOST"]

PORT_FLASK = app.config["PORT_FLASK"]

PORT_REACT = app.config["PORT_REACT"]
REACT_LINK=f"https://{HOST}:{PORT_REACT}"
CORS(app, supports_credentials=True, origins=REACT_LINK)

app.config["JWT_SECRET_KEY"] = "SECRET-KEY"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
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
@jwt_required(optional=True)
def account():

    if current_user:
        user_dict = current_user.get().to_dict() or {}

        return jsonify({
            "user":user_dict,
            })
    else:
        return jsonify({"user": None,})

@app.route("/api/char", methods = ["GET", "POST"])
def char():
    char = request.get_json()
    games = db.collection("section").stream()

    data = set()

    for game_doc in games:

        game = game_doc.to_dict()
        ch = game.get(char)
        if game["type"] == "Партия":
            data.add(ch)
    return list(data)

@app.route("/api/games", methods = ["GET", "POST"])
def games():
    filters = request.get_json()["filters"]
    games = db.collection("section").stream()

    data = []

    for game_doc in games:

        game = game_doc.to_dict()
        match = True

        for fil in list(filters.keys()):
            if fil == "have_places" and filters[fil]:
                if int(game.get("counter")) > 0:
                    match = match and True
                else:
                    match = False
            elif fil != "have_places" and filters[fil]:
                match = match and any((game.get(fil) == f for f in filters[fil]))
            else:
                pass
        
        if match and game.get("type") == "Партия" and get_time(game) < (datetime.today() + timedelta(hours=3)):
            game["id"] = game_doc.id
            data.append(game)

    return jsonify(data)

@app.route("/api/sections")
def sections():
    games = db.collection("section").stream()

    data = []
    for game_doc in games:
        game = game_doc.to_dict()
        if game.get("type") != "Партия" and get_time(game) < (datetime.today() + timedelta(hours=3)):
            game["id"] = game_doc.id
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
        users.append({"name": user.get("name"), "contact": user.get("contact"), "id": user.get("email")})

    game["users"] = users

    return jsonify(game)


@app.route('/api/main-info')
def main_info():
    info = db.collection('info').document('info').get().to_dict()
    response = {"date": info["date"], "address": info["address"], "description": info["description"]}

    return jsonify(response)

@app.route('/api/update-info', methods=["POST"])
@jwt_required()
def update_info():
    info_ref = db.collection('info').document('info')
    data = request.get_json()

    info_ref.update(data)
    return jsonify("ok")

@app.route('/api/users')
@jwt_required()
def users():
    if current_user.get().get("isAdmin") == False:
        return "Доступ запрещён", 403
    else:
        users = db.collection("users").stream()

        data = []
        for user in users:
            data.append(user.get("email"))

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
        return jsonify({"exists": True})

    
    user_info = {
        "email": email,
        "password": password,
        "name": name,
        "contact": contact,
        "image": image,
        "isAdmin": False,
        "isMaster": False,
        "sections": []
    }
    user = User(
            user_info["email"],
            user_info["password"],
            user_info["isAdmin"]
            )
    jwt_token = create_access_token(identity=user)

    token = generate_token(user_info)
    verify_code = randint(0, 100)
    send_verification_email(user_info["email"], verify_code)

    return jsonify({"exists": False, "code": verify_code})


@app.route("/api/verify", methods=["GET", "POST"])
def verify_email():

    form_data = request.get_json()
    email = form_data.get("email")
    password = form_data.get("password")
    name = form_data.get("name")
    contact = form_data.get("contact")
    image = ""

    user_info = {
        "email": email,
        "password": password,
        "name": name,
        "contact": contact,
        "image": image,
        "isAdmin": False,
        "isMaster": False,
        "sections": []
    }


    user_ref = db.collection("users").document(user_info["email"])

    user_ref.set(user_info)
    user_data = user_ref.get()

    user = User(
            user_data.get("email"),
            user_data.get("password"),
            user_data.get("isAdmin")
            )

    token = create_access_token(identity=user)

    return jsonify({"token": token})

@app.route("/api/enter", methods=["POST"])
def enter():
    form_data = request.get_json()
    user_data = db.collection("users").document(form_data["email"]).get()
    user_dict = user_data.to_dict()

    password_hash = form_data["password"]

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
    if not user_data["isAdmin"]:
        return "Доступ запрещён", 403

    form_data = request.form.to_dict()
    form_data["counter"] = int(form_data.get("counter", 0))
    form_data["places"] = int(form_data.get("places", 0))

    current_section = Section(form_data)

    if "image" in request.files:
        image = request.files["image"]
        image_path = f"/var/Geekmorolecon/images/games/{current_section.id}.jpg"
        image.save(image_path)
        current_section.image = f"/images/{current_section.id}.jpg"
    else:
        current_section.image = f"/images/blank.png"

    if not current_section.isExist():
        current_section.post()
    else:
        current_section.update(form_data)

    return jsonify({"id": current_section.id})

@app.route("/api/entryToSection", methods=["POST"])
@jwt_required()
def entryToSection():
    form_data = request.get_json()

    forUser, forSection = {}, {}
    user_time_date = []

    usersFrSection = db.collection('section').document(form_data['id']).get().to_dict()

    if int(usersFrSection['counter']) > 0:
        sectionsFrUser = current_user.get().to_dict()
        if form_data['id'] not in sectionsFrUser['sections']:

            for i in sectionsFrUser['sections']:
                doc = db.collection('section').document(i).get().to_dict()
                if doc:
                    time = doc['time']
                    date = doc['date']
                    user_time_date.append([time, date])
                
            if [usersFrSection['time'], usersFrSection['date']] not in user_time_date:
                sectionsFrUser['sections'].append(form_data['id'])

                forUser['sections'] = sectionsFrUser['sections']
                forSection['counter'] = str(int(usersFrSection['counter']) - 1)

                db.collection('section').document(form_data['id']).update(forSection)
                current_user.update(forUser)
            else:
                return jsonify("Cross")

    return jsonify("ok")

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

        return jsonify("ok")


@app.route('/api/update-section/<section_id>', methods=["POST"])
@jwt_required()
def updateSection(section_id):
    if current_user.get().get("isAdmin") == False:
        return "Доступ запрещён", 403
    else:
        update_data = request.get_json()
        db.collection('section').document(section_id).update(update_data)

        return update_data

@app.route('/api/delete-section/<section_id>', methods=["POST"])
@jwt_required()
def deleteSection(section_id):
    if current_user.get().get("isAdmin") == False:
        return "Доступ запрещён", 403
    else:
        users = db.collection('users').stream()
        print(section_id, type(section_id))

        for user in users:
            user_sections = user.get("sections")
            if section_id in user_sections:
                user_data = user.to_dict()
                print(user.get('email'))
                ind = user_sections.index(section_id)
                user_sections.pop(ind)
                user_data["sections"] = user_sections
                db.collection("users").document(user_data["email"]).update(user_data)

        db.collection('section').document(section_id).delete()

        return jsonify("ok")

@app.route("/api/logout")
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

def get_time(game):
    hour, minute = list(game["postTime"].strip('"').split(":"))
    day, month, year = list(game["postDate"].strip('"').split("."))
    hour = int(hour)
    minute = int(minute)
    day = int(day)
    month = int(month)
    year = int(year)

    return datetime(year=year, month=month, day=day, hour=hour, minute=minute)

if __name__ == "__main__":
    app.run(port = PORT_FLASK, ssl_context = ('www.geekmorolekon.ru_certificate.txt', 'www.geekmorolekon.ru_private.txt'))



