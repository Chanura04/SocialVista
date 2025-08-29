# blueprints/twitter/routes.py

import tweepy
from flask import Blueprint, request, session, flash, redirect, url_for, render_template
# Import your database and helper functions
from database import check_user_exists, check_api_details, check_canPost, get_pg_connection, \
    update_accountUpdatedOn_column
from helpers import APIKeyHandler, get_current_user_fernet_key

twitter_bp = Blueprint('x_platform', __name__)


@twitter_bp.route("/post_tweet", methods=["POST", "GET"])
def post_tweet():
    if request.method == "POST":
        if session.get("email"):
            if check_api_details():
                if check_user_exists(session['email']) and check_canPost():
                    UserData_conn = get_pg_connection()
                    cursor = UserData_conn.cursor()
                    cursor.execute(
                        "SELECT twitter_api_key,twitter_api_secret,twitter_access_token,twitter_access_token_secret,client_id,client_secret,screen_name FROM UserData WHERE Email = %s",
                        (session['email'],))
                    result = cursor.fetchone()

                    twitter_api_key = result[0]
                    twitter_api_secret = result[1]
                    twitter_user_access_token = result[2]
                    twitter_user_access_token_secret = result[3]

                    # Get the key from DB (stored as string)
                    fernet_key_str  = get_current_user_fernet_key()

                    # Convert back to bytes before using Fernet
                    fernet_key_bytes = fernet_key_str.encode()

                    api_key_handler_obj = APIKeyHandler(fernet_key=fernet_key_bytes)

                    decrypt_twitter_api_key=api_key_handler_obj.decrypt_key(twitter_api_key)
                    decrypt_twitter_api_secret=api_key_handler_obj.decrypt_key(twitter_api_secret)
                    decrypt_twitter_user_access_token=api_key_handler_obj.decrypt_key(twitter_user_access_token)
                    decrypt_twitter_user_access_token_secret=api_key_handler_obj.decrypt_key(twitter_user_access_token_secret)

                    print(f"""
                    \n\n  Fernet key: {fernet_key_bytes}
                        decrypt twitter api key: {decrypt_twitter_api_key}\n
                        decrypt twitter api secret: {decrypt_twitter_api_secret}\n
                        decrypt twitter user access token: {decrypt_twitter_user_access_token}\n
                        decrypt twitter user access token secret: {decrypt_twitter_user_access_token_secret}""")

                    if twitter_api_key and twitter_api_secret and twitter_user_access_token and twitter_user_access_token_secret:
                        client = tweepy.Client(
                            consumer_key=decrypt_twitter_api_key,
                            consumer_secret=decrypt_twitter_api_secret,
                            access_token=decrypt_twitter_user_access_token,
                            access_token_secret=decrypt_twitter_user_access_token_secret
                        )
                        texts = request.form.get("tweet_content")

                        try:
                            response = client.create_tweet(text=texts)
                            flash("🎉 Tweet posted successfully!")
                            print(response)
                            update_accountUpdatedOn_column(session['email'])

                        except Exception as e:
                            flash("Error posting tweet! Invalid API details...")
                            print(f"Error posting tweet: {e}")
                    else:
                        flash("⚠️ Please fill in the API details first!")
                else:
                    flash("⚠️ Please login or check your permissions first!")

            else:
                return redirect(url_for("x_platform.connect_twitter"))
        else:
            return redirect(url_for("auth.login"))
        # After POST (success or fail), always return something
    return render_template("post_content.html")

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


                print(f"""\n\nFernet key: {api_key_handler_obj} \n
                        encrypted Twitter key: {encrypted_twitter_api_key} \n
                        encrypted Twitter key secret: {encrypted_twitter_api_secret} \n
                        encrypted Client ID: {encrypted_client_id} \n
                        encrypted Client Secret: {encrypted_client_secret} \n\n""")



                UserData_conn = get_pg_connection()
                cursor = UserData_conn.cursor()
                cursor.execute(
                        """
                                   UPDATE UserData
                                   SET  twitter_api_key = %s,twitter_api_secret = %s,twitter_access_token = %s,twitter_access_token_secret = %s,
                                        client_id = %s,client_secret = %s ,screen_name = %s
                                   WHERE Email = %s
                                """,
                                   (
                                            encrypted_twitter_api_key,
                                            encrypted_twitter_api_secret,
                                            encrypted_twitter_access_token,
                                            encrypted_twitter_access_token_secret,
                                            encrypted_client_id,
                                            encrypted_client_secret,
                                            encrypted_screen_name,
                                            session['email'])
                                    )
                cursor.close()
                UserData_conn.commit()

                UserData_conn = get_pg_connection()
                cursor = UserData_conn.cursor()
                cursor.execute("""
                                        UPDATE UserData 
                                        SET isFilledApiDetails = %s , canPost = %s 
                                        WHERE Email = %s
                                      """,(isFilledApiDetails,canPost,session['email']))
                cursor.close()
                UserData_conn.commit()


                # tweets = get_user_tweets()
                # return redirect(url_for("dashboard"))
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
