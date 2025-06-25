from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from back.user import User, UserData
from back.section import Section
from back.create_table import import_data_to_file
from database.init_db import db

app = Flask("Reg")
app.secret_key = "your-very-secret-key"

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/', methods=["POST", "GET"])
def display_data():
    try:
        users_ref = db.collection('section')
        docs = users_ref.stream()
        data = [doc.to_dict() for doc in docs]

        print(current_user.isAdmin, current_user.is_authenticated)

        return render_template('index.html', data=data, 
                               is_admin=getattr(current_user, 'isAdmin', False), is_authenticated=current_user.is_authenticated)

    except Exception as e:
        return f"Ошибка получения данных: {str(e)}", 500


@app.route("/account")
@login_required
def account():
    # Получаем данные пользователя из Firestore
    user_data = db.collection("users").document(current_user.email).get()
    user_dict = user_data.to_dict() or {}

    # Получаем записи пользователя 
    entries_ref = db.collection("entries").where("user_email", "==", current_user.email).stream()
    entries = [entry.to_dict() | {"id": entry.id} for entry in entries_ref]

    return render_template(
        "profile.html",
        user=user_dict,
        entries=entries
    )



# filepath: c:\Users\user\Desktop\opencv\Vifiel.github.io\main.py
@app.route('/update-user', methods=['POST'])
@login_required
def update_user():
    user_ref = db.collection("users").document(current_user.email)
    updates = {}
    if 'name' in request.form:
        updates['name'] = request.form['name']
    if 'email' in request.form:
        updates['email'] = request.form['email']
    if 'password' in request.form and request.form['password']:
        import hashlib
        updates['password'] = hashlib.sha256(request.form['password'].encode("utf-8")).hexdigest()
    if updates:
        user_ref.update(updates)
    return redirect(url_for('account'))

@app.route('/add-entry', methods=['POST'])
@login_required
def add_entry():
    form_data = request.form.to_dict()
    db.collection("entries").add({
        "user_email": current_user.email,
        "title": form_data["title"],
        "content": form_data["content"]
    })
    return redirect(url_for('account'))

@app.route('/update-entry/<entry_id>', methods=['POST'])
@login_required
def update_entry(entry_id):
    form_data = request.form.to_dict()
    entry_ref = db.collection("entries").document(entry_id)
    entry_ref.update({
        "title": form_data["title"],
        "content": form_data["content"]
    })
    return redirect(url_for('account'))


@app.route('/delete-entry/<entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry_ref = db.collection("entries").document(entry_id)
    entry_ref.delete()
    return redirect(url_for('account'))







@app.route("/enter", methods=["POST"])
def enter():
    form_data = request.get_json()
    user_data = db.collection("users").document(form_data["email"]).get()
    user_dict = user_data.to_dict() or {}

    # user = User(form_data["email"], form_data["password"])
    # user_data = db.collection("users").document(user.email).get()

    import hashlib
    password_hash = hashlib.sha256(form_data["password"].encode("utf-8")).hexdigest()

    is_exist = user_data.exists 
    is_pass_match = user_data.get("password") == password_hash

    respond = jsonify({"exists": user_data.exists, "passMatch": is_pass_match})

    if not is_exist or not is_pass_match:
        return respond
    else:
        user = User(
            form_data["email"],
            user_dict.get("password"),
            is_admin=user_dict.get('isAdmin', False)
        )
        # login_user(current_user)
        login_user(user)
        return respond

@app.route("/createSection", methods=["POST"])
def createSection():

    user_data = db.collection("users").document(current_user.email).get()
    if not user_data.get("isAdmin", False):
        return "Доступ запрещён", 403
    
    form_data = request.form.to_dict()
    print(form_data)
    current_section = Section(form_data)
#    current_section.post()

    if not current_section.isExist():
        current_section.post()
        print('данные добавлены')
    else:
        current_section.update(form_data)
        print('данные обновлены')

    return redirect(url_for("display_data"))

@app.route("/entryToSection", methods=["POST"])
def entryToSection():
    form_data = request.form.to_dict()
    print(form_data)

    if current_user.is_authenticated:
        form_data['users'] = current_user.email
        print(form_data)

        forUser, forSection = {}, {}
        forUser['sections'] = form_data['name']
        forSection['users'] = form_data['users']

        db.collection('section').document(form_data['name']).set(forSection, merge=True)
        db.collection('users').document(form_data['users']).set(forUser, merge=True)

        print('пользователь добавлен')
    else:
        print('please log in')

    return redirect(url_for("display_data"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("display_data"))


@login_manager.user_loader
def load_user(user_id):
    # user_id - это email
    return User.get(user_id)

@app.route("/download")
def download():
    import_data_to_file()
    return send_file("static/files/registredUsers.xlsx", as_attachment=True)



if __name__ == "__main__":
    app.run()



