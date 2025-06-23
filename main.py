from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask("Reg")

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    email = request.form['email']
    password = request.form['pswd']
    print(password, email)
    return redirect(url_for("main"))

if __name__ == "__main__":
    app.run()
