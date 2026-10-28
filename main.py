from flask import Flask, render_template, request
from sqlalchemy import create_engine

from user import Base, create_signin_user

flask = Flask(__name__)
engine = create_engine("sqlite:///example.db")
Base.metadata.create_all(engine)

@flask.route("/")
def index():
    user = None
    error = ""

    return render_template("index.html", page="Home")

@flask.route("/base")
def base():
    return render_template("base.html", page="Base")

@flask.route("/login")
def login():
    return render_template("login.html", page="Login", error=error)

@flask.route("/account")
def account():
    return render_template("account.html", page="Account", user=user)

@flask.route("/create_login", methods=["POST"])
def create_login():
    global user, error

    action = request.form.get("action")
    email = request.form.get("email")
    password = request.form.get("password")
    feedback = create_signin_user(engine, action, email, password) # Returns JWT # Middleware
    error = feedback[0]

    if feedback[0] == "account created":
        user = feedback[1]
        error = ""
        return flask.redirect("/")
    elif feedback[0] == "email taken":
        return flask.redirect("/login")

    elif feedback[0] == "logged in":
        user = feedback[1]
        error = ""
        return flask.redirect("/")
    elif feedback[0] == "incorrect email":
        return flask.redirect("/login")
    elif feedback[0] == "incorrect password":
        return flask.redirect("/login")

if __name__ == "__main__":
    flask.run(host="127.0.0.1", port=5000, debug=True)