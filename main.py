from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from back.user import User, UserData
from back.section import Section
from database import init_db

app = Flask("Reg")

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def display_data():
    try:
        users_ref = init_db.db.collection('section')
        docs = users_ref.stream()
        data = []

        for doc in docs:
            doc_data = doc.to_dict()
            data.append(doc_data)

        return render_template('index.html', data=data)

    except Exception as e:
        return f"Ошибка получения данных: {str(e)}", 500

@app.route("/", methods=["POST", "GET"])
def main():
    return render_template("index.html", form_open=False)

@app.route("/register", methods=["POST"])
def register():
    form_data = request.get_json()
    user = UserData(form_data)

    db_user = init_db.db.collection("users").document(user.data["email"]).get()
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
    user_data = init_db.db.collection("users").document(user.email).get()
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


if __name__ == "__main__":
    app.run()



