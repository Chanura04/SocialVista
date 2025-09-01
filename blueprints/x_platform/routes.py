# blueprints/twitter/routes.py
from requests_oauthlib import OAuth1Session
import json
import tweepy
from flask import Blueprint, request, session, flash, redirect, url_for, render_template
# Import your database and helper functions
from database import check_user_exists, check_api_details, check_canPost, get_pg_connection, \
    update_accountUpdatedOn_column,add_X_api_details, store_future_cast_data,store_instant_cast_data,get_api_details,update_api_details_staus
from helpers import APIKeyHandler, get_current_user_fernet_key
from datetime import datetime
from celery_worker import post_future_tweet_task,post_instant_tweet_task
from zoneinfo import ZoneInfo
twitter_bp = Blueprint('x_platform', __name__)


# blueprints/twitter/routes.py

@twitter_bp.route("/instant_post_page", methods=["POST", "GET"])
def instant_post_page():
    if request.method == "POST":
        if session.get("email"):
            if check_api_details():
                if check_user_exists(session['email']) and check_canPost():
                    # UserData_conn = get_pg_connection()
                    # cursor = UserData_conn.cursor()
                    # cursor.execute(
                    #     "SELECT twitter_api_key,twitter_api_secret,twitter_access_token,twitter_access_token_secret,client_id,client_secret,screen_name FROM UserData WHERE Email = %s",
                    #     (session['email'],))
                    # result = cursor.fetchone()
                    result = get_api_details(session['email'])

                    twitter_api_key = result[0]
                    twitter_api_secret = result[1]
                    twitter_user_access_token = result[2]
                    twitter_user_access_token_secret = result[3]

                    fernet_key_str = get_current_user_fernet_key()
                    fernet_key_bytes = fernet_key_str.encode()
                    api_key_handler_obj = APIKeyHandler(fernet_key=fernet_key_bytes)

                    decrypt_twitter_api_key = api_key_handler_obj.decrypt_key(twitter_api_key)
                    decrypt_twitter_api_secret = api_key_handler_obj.decrypt_key(twitter_api_secret)
                    decrypt_twitter_user_access_token = api_key_handler_obj.decrypt_key(twitter_user_access_token)
                    decrypt_twitter_user_access_token_secret = api_key_handler_obj.decrypt_key(
                        twitter_user_access_token_secret)

                    tweet_content = request.form.get("tweet_content")
                    reply_settings = request.form.get("reply_settings_instantPosts")
                    platform_Name = "X"



                    update_accountUpdatedOn_column(session['email'])
                    if tweet_content and reply_settings:
                        # Schedule the task with the necessary data.
                        post_instant_tweet_task.delay(
                            session['email'],
                            platform_Name,
                            tweet_content,
                            reply_settings,
                            decrypt_twitter_api_key,
                            decrypt_twitter_api_secret,
                            decrypt_twitter_user_access_token,
                            decrypt_twitter_user_access_token_secret
                        )

                        return redirect(url_for("x_platform.instant_post_page"))
                    else:
                        flash("⚠️ Please fill the required fields!")
                        return redirect(url_for("x_platform.instant_post_page"))
                else:
                    flash("⚠️ Please login or check your permissions first!")
                    return redirect(url_for("auth.login"))
            else:
                return redirect(url_for("x_platform.connect_twitter"))
        else:
            return redirect(url_for("auth.login"))

    if request.method == "GET":
        if session.get("email"):
            if check_api_details():
                return render_template("send_instant_post.html")
            else:
                return redirect(url_for("x_platform.connect_twitter"))
        else:
            return redirect(url_for("auth.login"))

    return render_template("send_instant_post.html")

@twitter_bp.route("/connect_twitter", methods=["POST","GET"])
def connect_twitter():
    if request.method == "POST":
        if session.get("email"):
            if check_user_exists(session['email']):
                twitter_api_key = request.form.get("api_key")
                twitter_api_secret = request.form.get("api_secret")
                twitter_access_token = request.form.get("access_token")
                twitter_access_token_secret = request.form.get("access_token_secret")
                screen_name = request.form.get("screen_name")
                client_id = request.form.get("client_id")
                client_secret = request.form.get("client_secret")
                isFilledApiDetails=True
                canPost=True


                # Get the key from DB (stored as string)
                fernet_key_str = get_current_user_fernet_key() # make sure it's bytes thats why we encode that

                # Convert back to bytes before using Fernet
                fernet_key_bytes = fernet_key_str.encode()

                api_key_handler_obj = APIKeyHandler(fernet_key=fernet_key_bytes)

                encrypted_twitter_api_key=api_key_handler_obj.encrypt_key(twitter_api_key)
                encrypted_twitter_api_secret=api_key_handler_obj.encrypt_key(twitter_api_secret)
                encrypted_twitter_access_token=api_key_handler_obj.encrypt_key(twitter_access_token)
                encrypted_twitter_access_token_secret=api_key_handler_obj.encrypt_key(twitter_access_token_secret)
                encrypted_client_id=api_key_handler_obj.encrypt_key(client_id)
                encrypted_client_secret=api_key_handler_obj.encrypt_key(client_secret)
                encrypted_screen_name=api_key_handler_obj.encrypt_key(screen_name)

                # UserData_conn = get_pg_connection()
                # cursor = UserData_conn.cursor()
                # cursor.execute(
                #         """
                #                    UPDATE UserData
                #                    SET  twitter_api_key = %s,twitter_api_secret = %s,twitter_access_token = %s,twitter_access_token_secret = %s,
                #                         client_id = %s,client_secret = %s ,screen_name = %s
                #                    WHERE Email = %s
                #                 """,
                #                    (
                #                             encrypted_twitter_api_key,
                #                             encrypted_twitter_api_secret,
                #                             encrypted_twitter_access_token,
                #                             encrypted_twitter_access_token_secret,
                #                             encrypted_client_id,
                #                             encrypted_client_secret,
                #                             encrypted_screen_name,
                #                             session['email'])
                #                     )
                # cursor.close()
                # UserData_conn.commit()
                add_X_api_details(encrypted_twitter_api_key,
                                            encrypted_twitter_api_secret,
                                            encrypted_twitter_access_token,
                                            encrypted_twitter_access_token_secret,
                                            encrypted_client_id,
                                            encrypted_client_secret,
                                            encrypted_screen_name,
                                            session['email'])

                # UserData_conn = get_pg_connection()
                # cursor = UserData_conn.cursor()
                # cursor.execute("""
                #                         UPDATE UserData
                #                         SET isFilledApiDetails = %s , canPost = %s
                #                         WHERE Email = %s
                #                       """,(isFilledApiDetails,canPost,session['email']))
                # cursor.close()
                # UserData_conn.commit()
                update_api_details_staus(isFilledApiDetails,canPost,session['email'])

                return render_template("dashboard.html" )
            else:
                session['canPost'] = False
                return redirect(url_for("dashboard.dashboard"))
        else:
            return redirect(url_for("auth.login"))
    if request.method == "GET":
        if session.get("email"):
            if check_user_exists(session['email']):
                    redirect(url_for("api_details.get_api_details"))
        else:
            return redirect(url_for("auth.login"))

    return redirect(url_for("api_details.get_api_details"))

@twitter_bp.route("/choose_posting_method", methods=["GET"])
def choose_posting_method():
    if request.method == "GET":
        return  render_template("choose_posting_method.html")
    return render_template("choose_posting_method.html")



@twitter_bp.route("/future_post_page", methods=["POST", "GET"])
def future_post_page():
    if request.method == "POST":
        if session.get("email"):
            if check_api_details():
                if check_user_exists(session['email']) and check_canPost():
                    # UserData_conn = get_pg_connection()
                    # cursor = UserData_conn.cursor()
                    # cursor.execute(
                    #     "SELECT twitter_api_key,twitter_api_secret,twitter_access_token,twitter_access_token_secret,client_id,client_secret,screen_name FROM UserData WHERE Email = %s",
                    #     (session['email'],))
                    # result = cursor.fetchone()
                    result = get_api_details(session['email'])


                    twitter_api_key = result[0]
                    twitter_api_secret = result[1]
                    twitter_user_access_token = result[2]
                    twitter_user_access_token_secret = result[3]

                    # Get the key from DB (stored as string)
                    fernet_key_str = get_current_user_fernet_key()

                    # Convert back to bytes before using Fernet
                    fernet_key_bytes = fernet_key_str.encode()

                    api_key_handler_obj = APIKeyHandler(fernet_key=fernet_key_bytes)

                    decrypt_twitter_api_key = api_key_handler_obj.decrypt_key(twitter_api_key)
                    decrypt_twitter_api_secret = api_key_handler_obj.decrypt_key(twitter_api_secret)
                    decrypt_twitter_user_access_token = api_key_handler_obj.decrypt_key(twitter_user_access_token)
                    decrypt_twitter_user_access_token_secret = api_key_handler_obj.decrypt_key(
                        twitter_user_access_token_secret)


                    if twitter_api_key and twitter_api_secret and twitter_user_access_token and twitter_user_access_token_secret:

                        sri_lanka_tz = ZoneInfo("Asia/Colombo")

                        local_time = datetime.now(sri_lanka_tz)
                        created_on = local_time.strftime("%Y-%m-%d %H:%M:%S")

                        context = request.form.get("future_tweet_content")
                        need_to_publish = request.form.get("future_post_data_time")
                        reply_settings=request.form.get("reply_settings_schedulePosts")
                        print(F"reply settings: {reply_settings}")

                        # The format string should match how the date is stored in DB
                        future_post_data_time = datetime.strptime(need_to_publish, "%Y-%m-%dT%H:%M")
                        future_post_data_time = future_post_data_time.replace(tzinfo=sri_lanka_tz)

                        check_validity = future_post_data_time >= local_time  # True if future, False if past



                        if check_validity and context and need_to_publish:
                            try:
                                post_future_tweet_task.apply_async(args=[session['email'],need_to_publish, context,decrypt_twitter_api_key,decrypt_twitter_api_secret,decrypt_twitter_user_access_token,decrypt_twitter_user_access_token_secret,reply_settings], eta=future_post_data_time)
                                flash(f"🎉 Your tweet has been scheduled for {future_post_data_time}!", "success")
                                update_accountUpdatedOn_column(session['email'])

                                print(f"form data time: {need_to_publish}")
                                print(f"converted data time: {future_post_data_time}")
                                print(f"texts: {context}")
                                return redirect(url_for("x_platform.future_post_page"))
                            except Exception as e:

                                print(f"Error scheduling tweet: {e}")
                        else:
                            flash("⚠️ Please fill the required fields!")
                            return redirect(url_for("x_platform.future_post_page"))

                    else:
                        flash("⚠️ Please fill in the API details first!")

                else:
                    flash("⚠️ Please login or check your permissions first!")

            else:
                return redirect(url_for("x_platform.connect_twitter"))
        else:
            return redirect(url_for("auth.login"))
    if request.method == "GET":
        if session.get("email"):
            if check_api_details():
                return render_template("create_post_scheduler.html")
            else:
                return redirect(url_for("x_platform.connect_twitter"))
        else:
            return redirect(url_for("auth.login"))

        # After POST (success or fail), always return something
    # return redirect(url_for("auth.login"))
    return render_template("create_post_scheduler.html")
