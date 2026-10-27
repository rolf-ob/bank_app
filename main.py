from flask import Flask, render_template, request
from sqlalchemy import create_engine

from user import Base, create_user

flask = Flask(__name__)
engine = create_engine("sqlite:///example.db")
Base.metadata.create_all(engine)

@flask.route("/")
def index():
    return render_template("index.html", page="Home")

@flask.route("/base")
def base():
    return render_template("base.html", page="Base")

@flask.route("/login")
def login():
    return render_template("login.html", page="Login")

@flask.route("/create", methods=["POST"])
def create_account():
    name = request.form.get("email").split("@")[0]
    email = request.form.get("email")
    password = request.form.get("password")

    if create_user(engine, name, email, password):
        return flask.redirect("/")
    else:
        return flask.redirect("/login")

if __name__ == "__main__":
    flask.run(host="127.0.0.1", port=5000)