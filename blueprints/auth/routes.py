# blueprints/auth/routes.py
import os
import random
import string
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import uuid
import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
# Import your database and helper functions from a common module
from database import (add_new_user, get_user_password, get_user_first_name, check_user_exists, \
    update_accountUpdatedOn_column, update_accountCreatedOn_column,get_user_role,get_referral_code_owner,
                      add_referral_code_used_users,track_referralCode,update_user_role)

from helpers import Password
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
auth_bp = Blueprint('auth', __name__, template_folder='templates', static_folder='static')


@auth_bp.route("/login", methods=["POST", "GET"])
def login():
    #collect info from the login form
    #check if info in db
    if request.method == "POST":
        email = request.form.get("email")
        session['email']=email
        user_role = get_user_role(session['email'])
        session['role'] = user_role
        password = request.form.get("password")

        exists = check_user_exists(email)

        user_db_stored_password = get_user_password(email)
        print(user_db_stored_password)
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
                    promo_code=request.form.get("promo_code")
                    if promo_code:
                        check_promo_code=get_referral_code_owner(promo_code)
                        print("owner is ",check_promo_code)
                        if check_promo_code:

                            first_name = request.form.get("first_name")
                            last_name = request.form.get("last_name")
                            email = request.form.get("email")
                            password = request.form.get("password")
                            print("📌 DEBUG Signup values:", first_name, last_name, email, password)

                            session['signup_first_name'] = first_name
                            session['signup_last_name'] = last_name
                            session['signup_email'] = email
                            session['signup_password'] = password
                            session['referralCode'] = promo_code
                            print(session['referralCode'])

                            otp = ''.join(random.choices(string.digits, k=6))
                            session['otp'] = otp
                            print("OTP:", otp)

                            otp_expiry = datetime.now() + timedelta(seconds=50)
                            sender_email = "chanurakarunanayake12@gmail.com"
                            app_password = os.getenv("GMAIL_APP_PASSWORD")

                            # Build email
                            message = MIMEMultipart()
                            message["From"] = sender_email
                            message["To"] = session.get('signup_email')
                            message["Subject"] = "Your OTP Code"

                            # body = f"Your verification code is: {otp}"
                            # message.attach(MIMEText(body, "plain"))
                            body = f"Your verification code is: {otp}"
                            message.attach(MIMEText(body, "plain"))

                            try:
                                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                                    server.starttls()
                                    server.login(sender_email, app_password)
                                    server.sendmail(sender_email, session.get('signup_email'), message.as_string())
                                    session["otp_sent_message"] = True
                                    return redirect(url_for("auth.verify_email"))

                            except Exception as e:
                                logging.error(f"Error sending OTP: {e}")
                        else:
                            return render_template("signup.html",error="Invalid Promo Code...Please try again!")
                    else:
                        first_name = request.form.get("first_name")
                        last_name = request.form.get("last_name")
                        email = request.form.get("email")
                        password = request.form.get("password")
                        print("📌 DEBUG Signup values:", first_name, last_name, email, password)

                        session['signup_first_name'] = first_name
                        session['signup_last_name'] = last_name
                        session['signup_email'] = email
                        session['signup_password'] = password
                        session['referralCode'] = False

                        otp = ''.join(random.choices(string.digits, k=6))
                        session['otp'] = otp
                        print("OTP:", otp)

                        otp_expiry = datetime.now() + timedelta(seconds=50)
                        sender_email = "chanurakarunanayake12@gmail.com"
                        app_password = os.getenv("GMAIL_APP_PASSWORD")

                        # Build email
                        message = MIMEMultipart()
                        message["From"] = sender_email
                        message["To"] = session.get('signup_email')
                        message["Subject"] = "Your OTP Code"

                        # body = f"Your verification code is: {otp}"
                        # message.attach(MIMEText(body, "plain"))
                        body = f"Your verification code is: {otp}"
                        message.attach(MIMEText(body, "plain"))

                        try:
                            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                                server.starttls()
                                server.login(sender_email, app_password)
                                server.sendmail(sender_email, session.get('signup_email'), message.as_string())
                                session["otp_sent_message"] = True
                                return redirect(url_for("auth.verify_email"))

                        except Exception as e:
                            logging.error(f"Error sending OTP: {e}")


            except Exception as e:
                print(e)

    if request.method == "GET":
        return render_template("signup.html")
    return render_template("signup.html")


@auth_bp.route("/logout")
def logout():

        session.pop("username", None)
        session.pop("email", None)
        session.pop("toDashboard", False)
        session.clear()
        return redirect(url_for("auth.login"))

@auth_bp.route("/verify_email", methods=["POST", "GET"])
def verify_email():
    if request.method == "GET":
        return render_template("verify_email.html")
    if request.method == "POST":
        otp_password = request.form.get("otp_password")
        if session.get("otp_sent_message"):
            if otp_password==session.get('otp'):
                session['otp'] = None

                first_name = session.get('signup_first_name')
                last_name = session.get('signup_last_name')
                email = session.get('signup_email')
                password = session.get('signup_password')

                pass_obj = Password()
                encrypt_password = pass_obj.set_password(password)

                fernet_key = Fernet.generate_key()
                fernet_key_str = fernet_key.decode()

                account_status=True

                referralCode = str(uuid.uuid4())

                add_new_user(first_name, last_name, email, encrypt_password, fernet_key_str,referralCode,account_status)
                update_accountCreatedOn_column(email)

                if session.get('referralCode'):
                    referral_code_owner=get_referral_code_owner(session.get('referralCode'))
                    add_referral_code_used_users(referral_code_owner,session.get('signup_email'),session.get('referralCode'))

                    check_is_pro_user=track_referralCode(referral_code_owner)
                    print(check_is_pro_user)
                    if check_is_pro_user:
                        update_user_role(referral_code_owner,"pro_user")

                print("📌 DEBUG Signup values:", first_name, last_name, email, password)


                session["username"] = first_name
                return redirect(url_for("auth.login"))

            else:
                session['otp'] = None
                return render_template("verify_email.html", error="Invalid OTP...Please try again!")
        else:
            return redirect(url_for("auth.signup"))



