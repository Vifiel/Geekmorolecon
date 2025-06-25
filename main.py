from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from back.user import User, UserData
from back.section import Section
from back.create_table import import_data_to_file
from database.init_db import db

app = Flask("Reg")

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def display_data():
    try:
        users_ref = db.collection('section')
        docs = users_ref.stream()
        data = []

        for doc in docs:
            doc_data = doc.to_dict()
            data.append(doc_data)

        is_admin = False
        if current_user.is_authenticated:
            user_data = db.collection("users").document(current_user.email).get()
            is_admin = user_data.get("isAdmin", False)

        return render_template('index.html', data=data, is_admin=is_admin)

    except Exception as e:
        return f"Ошибка получения данных: {str(e)}", 500

@app.route("/", methods=["POST", "GET"])
def main():
    return render_template("index.html", form_open=False)

@app.route("/register", methods=["POST"])
def register():
    form_data = request.get_json()
    user = UserData(form_data)

    db_user = db.collection("users").document(user.data["email"]).get()
    respond = jsonify({"exists": db_user.exists})

    if db_user.exists:
        return respond
    else:
        user.post()
        return respond

@app.route("/enter", methods=["POST"])
def enter():
    form_data = request.get_json()

    user = User(form_data["email"], form_data["password"])
    user_data = db.collection("users").document(user.email).get()
    is_exist = user_data.exists 
    is_pass_match = user_data.get("password") == user.password
    respond = jsonify({"exists": user_data.exists, "passMatch": is_pass_match})

    if not is_exist or not is_pass_match:
        return respond
    else:
        login_user(current_user)
        return respond

@app.route("/createSection", methods=["POST"])
def createSection():
    
    if not current_user.is_authenticated:
        return "Пожалуйста, войдите в систему", 401

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

    return redirect(url_for("main"))

@app.route("/entryToSection", methods=["POST"])
@login_required
def entryToSection():
    form_data = request.form.to_dict()
    print(form_data)
    current_section = Section(form_data)
#    current_section.post()

    if not current_section.isExist():
        email = current_user.email
        current_section.post(email)

        print('пользователь добавлен')

    return redirect(url_for("main"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main"))


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



