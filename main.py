from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from back.section import Section
from back.user import User, UserData, Anonymous
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

@app.route('/api/', methods=["POST", "GET"])
def display_data():
    users_ref = db.collection('section')
    docs = users_ref.stream()
    data = [doc.to_dict() for doc in docs]

    return render_template('index.html', data=data, 
                            is_admin=getattr(current_user, 'isAdmin', False), is_authenticated=current_user.is_authenticated)

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token 
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        return response

@jwt.user_identity_loader
def user_identity_loader(user):
    return user.email

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.collection("users").document(id=identity)

@app.route("/api/account")
@jwt_required()
def account():
    # Получаем данные пользователя из Firestore
    user_data = db.collection("users").document(current_user.email).get()
    user_dict = user_data.to_dict() or {}

    # Получаем записи пользователя 
    entries_ref = db.collection("section").where( "users", "array_contains", current_user.email).stream()
    entries = []
    for entry in entries_ref:
        entries.append(entry.to_dict())
        entries[-1].update({"id": entry.id})

    return jsonify({
        "user":user_dict,
        "games":entries
        })

@app.route("/api/games")
def games():
    
    games = db.collection("section").stream()

    data = []
    for game in games:
        data.append(game.to_dict())

    return jsonify(data)

@app.route('/api/update-user', methods=['POST'])
@jwt_required()
def update_user():
    user_ref = db.collection("users").document(current_user.email)
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
            doc.get('password'),
            is_admin=doc.get('isAdmin', False)
        )

    return "ok"


@app.route('/api/delete-entry/<entry_id>', methods=['POST'])
def delete_entry(entry_id):
    email = current_user.email

    section_ref = db.collection("section").document(entry_id).get()
    section = section_ref.to_dict()
    
    ind = section["users"].index(email)
    section["users"].pop(ind)
    section["counter"] = str(int(section["counter"]) + 1)

    db.collection("section").document(entry_id).set(section)

    user_ref = db.collection("users").document(email).get()
    user = user_ref.to_dict()

    ind = user["sections"].index(entry_id)
    user["sections"].pop(ind)

    db.collection("users").document(email).set(user)

    return "ok"



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
    return jsonify({"exists": False})


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

    user_data = db.collection("users").document(current_user.email).get()
    if current_user.isAdmin == False:
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
def entryToSection():
    form_data = request.form.to_dict()

    if current_user.is_authenticated:
        form_data['email'] = current_user.email

        forUser, forSection = {}, {}

        usersFrSection = db.collection('section').document(form_data['name']).get().to_dict()
        sectionsFrUser = db.collection('users').document(form_data['email']).get().to_dict()

        if int(usersFrSection['counter']) > 0:
            if form_data['email'] not in usersFrSection['users'] and form_data['name'] not in sectionsFrUser['sections']:
                usersFrSection['users'].append(form_data['email'])
                sectionsFrUser['sections'].append(form_data['name'])

                forUser['sections'] = sectionsFrUser['sections']
                forSection['users'] = usersFrSection['users']
                forSection['counter'] = str(int(usersFrSection['counter']) - 1)

                db.collection('section').document(form_data['name']).set(forSection, merge=True)
                db.collection('users').document(form_data['email']).set(forUser, merge=True)

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



