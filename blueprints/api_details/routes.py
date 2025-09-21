# blueprints/api_details/routes.py

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from database import show_api_credentials_db, check_user_exists,add_X_api_details,update_api_details_staus,reset_api_details_db,get_is_filled_api_details
from helpers import get_current_user_fernet_key, APIKeyHandler
from decorators import has_role # Adjust the path if you placed it elsewhere
api_details_bp = Blueprint('api_details', __name__)



@api_details_bp.route("/connect", methods=["GET", "POST"])
def connect_twitter():
    if request.method == "POST":
        if session.get("email"):
            if get_is_filled_api_details(session['email']):
                return redirect(url_for("dashboard.dashboard"))


            if check_user_exists(session['email'])   :
                twitter_api_key = request.form.get("api_key")
                twitter_api_secret = request.form.get("api_secret")
                twitter_access_token = request.form.get("access_token")
                twitter_access_token_secret = request.form.get("access_token_secret")
                screen_name = request.form.get("screen_name")
                client_id = request.form.get("client_id")
                client_secret = request.form.get("client_secret")
                isFilledApiDetails=True
                canPost=True
                print("DHow",twitter_api_key)


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
                add_X_api_details(session['email'],encrypted_twitter_api_key,
                                            encrypted_twitter_api_secret,
                                            encrypted_twitter_access_token,
                                            encrypted_twitter_access_token_secret,
                                            encrypted_client_id,
                                            encrypted_client_secret,
                                            encrypted_screen_name,
                                  isFilledApiDetails,canPost
                                            )

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

                return redirect(url_for("dashboard.dashboard"))
            else:
                session['canPost'] = False
                return redirect(url_for("dashboard.dashboard"))
        else:
            return redirect(url_for("auth.login"))
    if request.method == "GET":
        if session.get("email"):
            if check_user_exists(session['email']):
                return render_template('get_api_details.html')

        else:
            return redirect(url_for("auth.login"))

    return redirect(url_for("api_details.connect_twitter"))

# @api_details_bp.route("/connect", methods=["GET", "POST"])
# def connect_twitter():
#     if request.method == "POST":
#         if session.get("email"):
#             if check_user_exists(session['email']):
#                 twitter_api_key = request.form.get("api_key")
#                 twitter_api_secret = request.form.get("api_secret")
#                 twitter_access_token = request.form.get("access_token")
#                 twitter_access_token_secret = request.form.get("access_token_secret")
#                 screen_name = request.form.get("screen_name")
#                 client_id = request.form.get("client_id")
#                 client_secret = request.form.get("client_secret")
#                 isFilledApiDetails=True
#                 canPost=True
#
#
#                 # Get the key from DB (stored as string)
#                 fernet_key_str = get_current_user_fernet_key() # make sure it's bytes thats why we encode that
#
#                 # Convert back to bytes before using Fernet
#                 fernet_key_bytes = fernet_key_str.encode()
#
#                 api_key_handler_obj = APIKeyHandler(fernet_key=fernet_key_bytes)
#
#                 encrypted_twitter_api_key=api_key_handler_obj.encrypt_key(twitter_api_key)
#                 encrypted_twitter_api_secret=api_key_handler_obj.encrypt_key(twitter_api_secret)
#                 encrypted_twitter_access_token=api_key_handler_obj.encrypt_key(twitter_access_token)
#                 encrypted_twitter_access_token_secret=api_key_handler_obj.encrypt_key(twitter_access_token_secret)
#                 encrypted_client_id=api_key_handler_obj.encrypt_key(client_id)
#                 encrypted_client_secret=api_key_handler_obj.encrypt_key(client_secret)
#                 encrypted_screen_name=api_key_handler_obj.encrypt_key(screen_name)
#
#
#                 print(f"""\n\nFernet key: {api_key_handler_obj} \n
#                         encrypted Twitter key: {encrypted_twitter_api_key} \n
#                         encrypted Twitter key secret: {encrypted_twitter_api_secret} \n
#                         encrypted Client ID: {encrypted_client_id} \n
#                         encrypted Client Secret: {encrypted_client_secret} \n\n""")
#
#
#
#                 UserData_conn = get_pg_connection()
#                 cursor = UserData_conn.cursor()
#                 cursor.execute(
#                         """
#                                    UPDATE UserData
#                                    SET  twitter_api_key = %s,twitter_api_secret = %s,twitter_access_token = %s,twitter_access_token_secret = %s,
#                                         client_id = %s,client_secret = %s ,screen_name = %s
#                                    WHERE Email = %s
#                                 """,
#                                    (
#                                             encrypted_twitter_api_key,
#                                             encrypted_twitter_api_secret,
#                                             encrypted_twitter_access_token,
#                                             encrypted_twitter_access_token_secret,
#                                             encrypted_client_id,
#                                             encrypted_client_secret,
#                                             encrypted_screen_name,
#                                             session['email'])
#                                     )
#                 cursor.close()
#                 UserData_conn.commit()
#
#                 UserData_conn = get_pg_connection()
#                 cursor = UserData_conn.cursor()
#                 cursor.execute("""
#                                         UPDATE UserData
#                                         SET isFilledApiDetails = %s , canPost = %s
#                                         WHERE Email = %s
#                                       """,(isFilledApiDetails,canPost,session['email']))
#                 cursor.close()
#                 UserData_conn.commit()
#
#
#                 # tweets = get_user_tweets()
#                 return redirect(url_for("dashboard.dashboard"))
#
#             else:
#                 session['canPost'] = False
#                 return redirect(url_for("dashboard.dashboard"))
#         else:
#             return redirect(url_for("login"))
#     if request.method == "GET":
#         if session.get("email"):
#             if check_user_exists(session['email']):
#                     redirect(url_for("api_details.get_api_details"))
#         else:
#             return redirect(url_for("auth.login"))
#
#     return redirect(url_for("api_details.get_api_details"))
#

@api_details_bp.route("/reset_api_details" )

def reset_api_details():

        if check_user_exists(session['email']):
            # client_id = None
            # client_secret = None
            # twitter_access_token = None
            # twitter_access_token_secret = None
            # twitter_api_key = None
            # twitter_api_secret = None
            # screen_name = None
            # isFilledApiDetails=False
            # canPost=False
            #
            # UserData_conn = get_pg_connection()
            # cursor = UserData_conn.cursor()
            # cursor.execute("""
            #                UPDATE UserData
            #                SET twitter_api_key             = %s,
            #                    twitter_api_secret          = %s,
            #                    twitter_access_token        = %s,
            #                    twitter_access_token_secret = %s,
            #                    client_id                   = %s,
            #                    client_secret               = %s,
            #                    screen_name                 = %s
            #                WHERE Email = %s""",
            #                (twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret,
            #                 client_id, client_secret, screen_name, session['email']))
            # cursor.close()
            # UserData_conn.commit()
            reset_api_details_db(session['email'])

            # UserData_conn = get_pg_connection()
            # cursor = UserData_conn.cursor()
            # cursor.execute("""
            #                UPDATE UserData
            #                SET isFilledApiDetails = %s,canPost = %s
            #                WHERE Email = %s
            #                """, (isFilledApiDetails, canPost, session['email']))
            # cursor.close()
            # UserData_conn.commit()
            return redirect(url_for("api_details.show_api_credentials"))
        else:
            return redirect(url_for("auth.login"))





@api_details_bp.route("/show_credentials")

def show_api_credentials():
    if session.get('email'):

        if check_user_exists(session['email']):
            if get_is_filled_api_details(session['email']):

                #
                # UserData_conn = get_pg_connection()
                # cursor = UserData_conn.cursor()
                # cursor.execute("""
                #                SELECT twitter_api_key,
                #                       twitter_api_secret,
                #                       twitter_access_token,
                #                       twitter_access_token_secret,
                #                       client_id,
                #                       client_secret,
                #                       screen_name,
                #                       isFilledApiDetails,
                #                       canPost
                #                FROM UserData
                #                WHERE Email = %s""",
                #                (session['email'],))
                result = show_api_credentials_db(session['email'])
                twitter_api_key = result[0]
                twitter_api_secret = result[1]
                twitter_access_token = result[2]
                twitter_access_token_secret = result[3]
                client_id = result[4]
                client_secret = result[5]
                screen_name = result[6]
                isFilledApiDetails=result[7]
                canPost=result[8]

                if client_id and client_secret and twitter_api_key and twitter_api_secret and twitter_access_token and twitter_access_token_secret and screen_name:
                    # Get the key from DB (stored as string)
                    fernet_key_str = get_current_user_fernet_key()

                    # Convert back to bytes before using Fernet
                    fernet_key_bytes = fernet_key_str.encode()

                    api_key_handler_obj = APIKeyHandler(fernet_key=fernet_key_bytes)

                    decrypt_twitter_api_key = api_key_handler_obj.decrypt_key(twitter_api_key)
                    decrypt_twitter_api_secret = api_key_handler_obj.decrypt_key(twitter_api_secret)
                    decrypt_twitter_user_access_token = api_key_handler_obj.decrypt_key(twitter_access_token)
                    decrypt_twitter_user_access_token_secret = api_key_handler_obj.decrypt_key(twitter_access_token_secret)
                    decrypt_client_id= api_key_handler_obj.decrypt_key(client_id)
                    decrypt_client_secret = api_key_handler_obj.decrypt_key(client_secret)
                    decrypt_screen_name = api_key_handler_obj.decrypt_key(screen_name)

                    if isFilledApiDetails and canPost:
                        return render_template("show_api_details.html",
                                               screen_name=decrypt_screen_name,
                                               client_id=decrypt_client_id,
                                               client_secret=decrypt_client_secret,
                                               user_access_token=decrypt_twitter_user_access_token,
                                               user_access_token_secret=decrypt_twitter_user_access_token_secret,
                                               twitter_api_key=decrypt_twitter_api_key,
                                               twitter_api_secret=decrypt_twitter_api_secret
                                               )


                    else:
                        flash("Please fill the API details!")
                        return render_template("show_api_details.html",
                                               screen_name=None,
                                               client_id=None,
                                               client_secret=None,
                                               user_access_token=None,
                                               user_access_token_secret=None,
                                               twitter_api_key=None,
                                               twitter_api_secret=None
                                               )
                else:
                    return redirect(url_for("api_details.connect_twitter"))
            else:
                return redirect(url_for("api_details.connect_twitter"))
        else:
            flash("Please login first!")
            return render_template("show_api_details.html",
                                   screen_name=None,
                                   client_id=None,
                                   client_secret=None,
                                   user_access_token=None,
                                   user_access_token_secret=None,
                                   twitter_api_key=None,
                                   twitter_api_secret=None
                                   )

    else:
        return redirect(url_for("auth.login"))


# @api_details_bp.route("/get_api_details")
# def get_api_details():
#     return render_template("get_api_details.html")
