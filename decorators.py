# decorators.py

from functools import wraps
from flask import session, redirect, url_for, flash
from database import get_pg_connection


# This decorator checks if the current user has the required role
def has_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('email'):
                flash("Please log in to access this page.", "danger")
                return redirect(url_for('auth.login'))

            conn = get_pg_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM UserData WHERE email = %s", (session['email'],))
            result = cursor.fetchone()
            conn.close()

            user_role = result[0] if result else 'user'

            # Here's the core logic: check if the user's role is in the list of allowed roles
            # We can define a hierarchy, e.g., admin can do everything
            role_hierarchy = {
                'admin': ['admin', 'moderator', 'user'],
                'moderator': ['moderator', 'user'],
                'user': ['user']
            }

            if user_role not in role_hierarchy or required_role not in role_hierarchy[user_role]:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for('dashboard.dashboard'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator