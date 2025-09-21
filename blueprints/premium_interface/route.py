
from flask import Blueprint, render_template,session
from database import get_currentUser_referred_count
premium_interface_bp = Blueprint("premium_interface", __name__,template_folder="templates",static_folder="static")

@premium_interface_bp.route('/premium_interface')
def premium_interface():
    currentUser_referred_count=get_currentUser_referred_count(session.get('email'))
    print(currentUser_referred_count)
    user_role = session.get('role', 'user')

    return render_template('user_premium_section.html',currentUser_referred_count=currentUser_referred_count,role=user_role)