import os

from flask import Flask, render_template, request, make_response
from sqlalchemy import create_engine

from user import Base, create_user, login_user, create_jwt_token, verify_token

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Set secret environment variable: $env:JWT_SECRET_KEY = \"key\"")

flask = Flask(__name__)
engine = create_engine("sqlite:///users.db")
Base.metadata.create_all(engine)

@flask.route("/")
def index():
    return render_template("index.html", title="Home")

@flask.route("/base")
def base():
    return render_template("base.html", title="Base")

@flask.route("/login")
def login():
    return render_template("login.html", title="Login")

@flask.route("/account")
def account():

    return render_template("account.html", title="Account")

@flask.route("/create_login", methods=["POST"])
def create_login():
    action = request.form.get("action")
    email = request.form.get("email")
    password = request.form.get("password")

    if action == "create account":
        user = create_user(engine, email, password)
    elif action == "log in":
        user = login_user(engine, email, password)

    if user:
        token = create_jwt_token(SECRET_KEY, user.id)
        resp = flask.redirect("/")
        resp.set_cookie(
            "token",
            token,
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=3600
        )
        return resp
    
    else:
        return flask.redirect("/login")

if __name__ == "__main__":
    flask.run(host="127.0.0.1", port=5000, debug=True)