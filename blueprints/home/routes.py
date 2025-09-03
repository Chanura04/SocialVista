
from flask import Blueprint, render_template, session, current_app, redirect, url_for

home_bp = Blueprint('home', __name__, template_folder='templates', static_folder='static')

@home_bp.route("/")
def home():
    if session.get("reset_token") != current_app.config["SESSION_RESET_TOKEN"]:
        session.clear()
        session["reset_token"] = current_app.config["SESSION_RESET_TOKEN"]

    if session.get("username"):
        user_role = session.get('role', 'user')
        return render_template("home.html", username=session.get('username'), role=user_role)
    else:
      return render_template("home.html")
