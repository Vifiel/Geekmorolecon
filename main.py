from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import hashlib

app = Flask("Reg")

class User:
    def __init__(self, email, password):
        self.password = hashlib.sha256(password.encode("utf-8")).hexdigest()
        self.email = email
    

class UserData(User):
    def __init__(self, email, password, name):
        super().__init__(email, password)
        self.name = name





@app.route("/")
def main():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    form_data = request.form.to_dict()
    user = UserData(form_data['email'], form_data['pswd'], form_data['name'])
    return redirect(url_for("main"))

if __name__ == "__main__":
    app.run()
