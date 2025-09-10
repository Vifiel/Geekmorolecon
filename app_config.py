from flask import Flask

app = Flask("Reg")
app.config.from_pyfile("config.py")
