import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, flash, url_for
from sqlalchemy import create_engine

from user import Base, create_user, log_into_user, create_jwt_token, get_user_by_token

flask = Flask(__name__)
engine = create_engine("sqlite:///users.db")
Base.metadata.create_all(engine)

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Set secret environment variable: $env:JWT_SECRET_KEY = \"key\"")

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
    return render_template("index.html", title="Home")

@flask.route("/base")
def base():
    return render_template("base.html", title="Base")

@flask.route("/sign_in")
def sign_in():
    return render_template("sign_in.html", title="Sign In")

@flask.route("/log_in")
def log_in():
    return render_template("log_in.html", title="Log In")

@flask.route("/account")
def account():
    return render_template("account.html", title="Account")

@flask.route("/create_account", methods=["POST"])
def create_account():
    email = request.form.get("email")
    password = request.form.get("password")
    user = create_user(engine, email, password)

    if user:
        token = create_jwt_token(SECRET_KEY, user.id)
        resp = redirect("/")
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
        flash("Email already belongs to an account", "error")
        return redirect("/sign_in")

@flask.route("/log_into_account", methods=["POST"])
def log_into_account():
    email = request.form.get("email")
    password = request.form.get("password")
    user = log_into_user(engine, email, password)

    if user:
        token = create_jwt_token(SECRET_KEY, user.id)
        resp = redirect("/")
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

if __name__ == "__main__":
    flask.run(host="127.0.0.1", port=5000, debug=True)