# blueprints/dashboard/routes.py

from flask import Blueprint, render_template, session, current_app

dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates', static_folder='static')

@dashboard_bp.route("/")
def dashboard():
    if session.get("reset_token") != current_app.config["SESSION_RESET_TOKEN"]:
        session.clear()
        session["reset_token"] = current_app.config["SESSION_RESET_TOKEN"]

    if session.get("username") and session.get("toDashboard"):
        return render_template("dashboard.html", username=session.get('username'))
    else:
        return render_template("dashboard.html")