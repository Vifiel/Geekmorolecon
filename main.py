from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask("Reg")

@app.route("/")
def main():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
