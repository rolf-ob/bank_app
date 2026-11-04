import os

from decimal import Decimal
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, flash, url_for
from sqlalchemy import create_engine

from user import Base, User, create_new_user, login_as_user, delete_user, create_jwt_token, get_user_by_token, verify_password
from account import Account, get_user_accounts, get_user_account, rename_account, delete_account

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
    if user:
        accounts = get_user_accounts(engine, user)
        total = sum((account.balance for account in accounts), Decimal("0.00"))
        account_id = request.args.get("account_id", type=int)

        if account_id:
            account = get_user_account(engine, user, account_id)
        else:
            account = None
    
    else:
        accounts = []
        total = Decimal("0.00")
        account_id = None
        account = None

    return render_template(
        "index.html",
        title="Home",
        user=user,
        total=total,
        accounts=accounts,
        open_account=account
    )

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
    user = login_as_user(engine, email, password)

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

@flask.route("/rename_account_route", methods=["POST"])
def rename_account_route():
    account_id = request.form.get("account_id", type=int)
    new_name = request.form.get("new_name")
    user = get_current_user()

    if not user:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    if rename_account(engine, user, account_id, new_name):
        flash("Account renamed", "success")
    else:
        flash("Invalid name", "error")
    
    return redirect(url_for("index"))

@flask.route("/delete_account_route", methods=["POST"])
def delete_account_route():
    user = get_current_user()

    if not user:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))

    account_id = request.form.get("account_id", type=int)
    password = request.form.get("password", "")

    if account_id is None or not password:
        flash("Invalid request.", "error")

    if not verify_password(user.password_hash, password):
        flash("Incorrect password.", "error")

    if delete_account(engine, user, account_id):
        flash("Account deleted", "success")
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    flask.run(host="127.0.0.1", port=5000, debug=True)