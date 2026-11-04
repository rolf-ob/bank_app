import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, flash, url_for
from sqlalchemy import create_engine

from user import Base, User, create_new_user, log_into_user, delete_user, create_jwt_token, get_user_by_token
from account import Account, get_user_accounts, create_account

flask = Flask(__name__)
engine = create_engine("sqlite:///users.db")
Base.metadata.create_all(engine)

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Set secret environment variable: $env:JWT_SECRET_KEY = \"key\" from generated key: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")

flask.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
if not flask.config["SECRET_KEY"]:
    raise RuntimeError("Set secret flask environment variable: $env:FLASK_SECRET_KEY = \"key\"")

def get_current_user():
    token = request.cookies.get("token")
    if token:
        return get_user_by_token(engine, SECRET_KEY, token)
    return None

@flask.context_processor
def inject_user():
    return {"current_user": get_current_user()}

@flask.route("/")
def index():

    user = get_current_user()
    accounts = get_user_accounts(engine, user) if user else []

    if user:
        create_account(engine, user, "my account")

    return render_template("index.html", title="Home", user=user, accounts=accounts)

@flask.route("/base")
def base():
    return render_template("base.html", title="Base")

@flask.route("/sign_in")
def sign_in():
    return render_template("sign_in.html", title="Sign In")

@flask.route("/log_in")
def log_in():
    return render_template("log_in.html", title="Log In")

@flask.route("/user")
def user():
    return render_template("user.html", title="User")

@flask.route("/create_user", methods=["POST"])
def create_user():
    email = request.form.get("email")
    password = request.form.get("password")
    user = create_new_user(engine, email, password)

    if user:
        token = create_jwt_token(SECRET_KEY, user.id)
        resp = redirect(url_for("index"))
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
        flash("Email already belongs to a user", "error")
        return redirect(url_for("sign_in"))

@flask.route("/log_into_user", methods=["POST"])
def log_into_user():
    email = request.form.get("email")
    password = request.form.get("password")
    user = log_into_user(engine, email, password)

    if user:
        token = create_jwt_token(SECRET_KEY, user.id)
        resp = redirect(url_for("index"))
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
        flash("Invalid email or password", "error")
        return redirect(url_for("log_in"))

@flask.route("/log_out", methods=["POST"])
def log_out():
    resp = redirect(url_for("log_in"))
    resp.delete_cookie("token")
    return resp

@flask.route("/delete_user", methods=["POST"])
def delete_user():
    password = request.form.get("password")

    resp = redirect(url_for("index"))
    resp.delete_cookie("token")

    if delete_user(engine, get_current_user(), password):
        return resp

    else:
        flash("Invalid password", "error")
        return redirect(url_for("user"))

if __name__ == "__main__":
    flask.run(host="127.0.0.1", port=5000, debug=True)