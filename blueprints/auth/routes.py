# blueprints/auth/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
# Import your database and helper functions from a common module
from database import get_pg_connection, get_user_password, get_user_first_name, check_user_exists, \
    update_accountUpdatedOn_column, update_accountCreatedOn_column
from helpers import Password
from cryptography.fernet import Fernet
auth_bp = Blueprint('auth', __name__, template_folder='templates', static_folder='static')

class Password:
    def set_password(self,password):
        self.password = generate_password_hash(password)
        return self.password

    def check_password(self,hashed_password, plain_password):
        return check_password_hash(hashed_password, plain_password)

@auth_bp.route("/login", methods=["POST", "GET"])
def login():
    #collect info from the login form
    #check if info in db
    if request.method == "POST":
        email = request.form.get("email")
        session['email']=email
        password = request.form.get("password")

        exists = check_user_exists(email)

        user_db_stored_password = get_user_password(email)
        pass_ob=Password()




        if exists:
            session['email']=email
            if pass_ob.check_password(user_db_stored_password,password) :
                first_name = get_user_first_name(email)
                print(first_name)
                session['username'] = first_name
                session['toDashboard'] = True
                update_accountUpdatedOn_column(session['email'])
                return redirect(url_for("dashboard.dashboard"))
            else:
                return render_template("login.html", error="Invalid Password...Please try again!",email=session['email'])

        else:
            # otherwise show homepages
            return render_template("login.html",error="User does not exist...Please signup first!")
    if request.method == "GET":
        return render_template("login.html",error="")


@auth_bp.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        exists = check_user_exists(email)
        if email:
            try:

                if exists:
                    return render_template("login.html", error="username already exists here!")

                else:

                    first_name = request.form.get("first_name")
                    last_name = request.form.get("last_name")
                    email = request.form.get("email")
                    password = request.form.get("password")
                    print("📌 DEBUG Signup values:", first_name, last_name, email, password)

                    pass_obj = Password()
                    encrypt_password = pass_obj.set_password(password)

                    fernet_key = Fernet.generate_key()
                    fernet_key_str = fernet_key.decode()

                    UserData_conn = get_pg_connection()
                    cursor = UserData_conn.cursor()
                    cursor.execute("""
                                   INSERT INTO UserData (FirstName, LastName, Email, Password, Fernet_key)
                                   VALUES (%s, %s, %s, %s, %s)
                                   """, (first_name, last_name, email, encrypt_password, fernet_key_str,))
                    cursor.close()
                    UserData_conn.commit()
                    update_accountCreatedOn_column(email)

                    UserData_conn = get_pg_connection()
                    cursor = UserData_conn.cursor()
                    cursor.execute("""
                                   UPDATE UserData
                                   SET signup_status= %s,
                                       account_status= %s
                                   WHERE Email = %s


                                   """, (True, True, email))
                    cursor.close()
                    UserData_conn.commit()

                    session["username"] = first_name
                    return redirect(url_for("auth.login"))
            except Exception as e:
                print(e)

    if request.method == "GET":
        return render_template("signup.html")
    return render_template("signup.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    if request.method == "POST":
        session.pop("username", None)
        session.pop("email", None)
        session.pop("toDashboard", False)
        session.clear()
        return redirect(url_for("auth.login"))
    return redirect(url_for("dashboard.dashboard"))