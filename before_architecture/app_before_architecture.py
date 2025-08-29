#request use for get and post request in database
#redirect for different pages
#generate_password_hash,check_password_hash password encrypting and decrypting
import email
import os,glob
from datetime import datetime
import pytz
from flask import Flask,render_template,request,redirect,session,url_for,flash
from werkzeug.security import generate_password_hash,check_password_hash
import tweepy
from cryptography.fernet import Fernet
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key="123"

import uuid
app.config["SESSION_RESET_TOKEN"] = str(uuid.uuid4())


def clear_session_files():
    for file in glob.glob("flask_session/*"):
        os.remove(file)

clear_session_files()


def get_pg_connection():
    conn = psycopg2.connect(
        host= os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")


    )

    return conn

class Password:
    def set_password(self,password):
        self.password = generate_password_hash(password)
        return self.password

    def check_password(self,hashed_password, plain_password):
        return check_password_hash(hashed_password, plain_password)


class APIKeyHandler:

    def __init__(self,fernet_key):
        self.fernet_key = fernet_key
        self.cipher = Fernet(self.fernet_key)

    def encrypt_key(self, key):
        return self.cipher.encrypt(key.encode()).decode()

    def decrypt_key(self, encrypted_key):
        return self.cipher.decrypt(encrypted_key.encode()).decode()

@app.route("/")
def dashboard():
    if session.get("reset_token") != app.config["SESSION_RESET_TOKEN"]:
        session.clear()
        session["reset_token"] = app.config["SESSION_RESET_TOKEN"]

    if session.get("username") and session.get("toDashboard"):
        return render_template("dashboard.html", username=session.get('username'))
    else:
        return render_template("dashboard.html")

def get_user_password(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT Password FROM UserData WHERE Email = %s", (email,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_user_first_name(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT FirstName FROM UserData WHERE Email = %s", (email,))
    result = cursor.fetchone()
    return result[0] if result else None

def check_user_exists(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT 1 FROM UserData WHERE Email = %s ",(email,))
    exists = cursor.fetchone()
    return exists is not None


def update_accountUpdatedOn_column(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    local_time = datetime.now()
    cursor.execute("UPDATE UserData SET account_updated_on= %s WHERE Email = %s", (local_time.strftime("%Y-%m-%d %H:%M:%S"),email))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()

def update_accountCreatedOn_column(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    local_time = datetime.now()
    cursor.execute("UPDATE UserData SET account_created_on= %s WHERE Email = %s", (local_time.strftime("%Y-%m-%d %H:%M:%S"),email))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()


def check_api_details():
    # user = User.query.filter_by(email=session['email']).first()
    if check_user_exists(session['email']):

        UserData_conn = get_pg_connection()
        cursor = UserData_conn.cursor()
        cursor.execute("SELECT twitter_api_key,twitter_api_secret,twitter_access_token,twitter_access_token_secret,client_id,client_secret,screen_name FROM UserData WHERE Email = %s", (session['email'],))
        result = cursor.fetchone()

        twitter_api_key = result[0]
        twitter_api_secret = result[1]
        twitter_user_access_token = result[2]
        twitter_user_access_token_secret = result[3]
        client_id = result[4]
        client_secret = result[5]
        screen_name = result[6]

        if not client_id or not client_secret or not twitter_api_key or not twitter_api_secret or not twitter_user_access_token or not twitter_user_access_token_secret or not screen_name:
            print("api details not filled...redirecting to get api details page...!")
            return False
        else:
            return True
    else:
        return False

#Login
@app.route("/login",methods=["POST","GET"])
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
                return redirect(url_for("dashboard"))
            else:
                return render_template("login.html", error="Invalid Password...Please try again!", email=session['email'])

        else:
            # otherwise show homepages
            return render_template("login.html", error="User does not exist...Please signup first!")
    if request.method == "GET":
        return render_template("login.html", error="")


#register
@app.route("/signup",methods=["POST","GET"])
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

                    pass_obj=Password()
                    encrypt_password=pass_obj.set_password(password)

                    fernet_key = Fernet.generate_key()
                    fernet_key_str = fernet_key.decode()

                    UserData_conn=get_pg_connection()
                    cursor=UserData_conn.cursor()
                    cursor.execute("""
                                            INSERT INTO UserData (FirstName,LastName,Email,Password,Fernet_key)
                                            VALUES (%s,%s,%s,%s,%s)
                                        """,(first_name,last_name,email,encrypt_password,fernet_key_str,))
                    cursor.close()
                    UserData_conn.commit()
                    update_accountCreatedOn_column(email)

                    UserData_conn=get_pg_connection()
                    cursor=UserData_conn.cursor()
                    cursor.execute("""
                            UPDATE UserData
                            SET signup_status= %s , account_status= %s
                            WHERE Email = %s
                    
                    
                    """,(True,True,email))
                    cursor.close()
                    UserData_conn.commit()

                    session["username"] = first_name
                    return redirect(url_for("login"))
            except Exception as e:
                print(e)

    if request.method == "GET":
        return render_template("signup.html")
    return render_template("signup.html")



def check_canPost():
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT canPost FROM UserData WHERE Email = %s", (session['email'],))
    result = cursor.fetchone()
    return result[0] is not None

@app.route("/post_tweet", methods=["POST", "GET"])
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
                return redirect(url_for("connect_twitter"))
        else:
            return redirect(url_for("login"))
        # After POST (success or fail), always return something
    return render_template("post_content.html")


def check_isFilledApiDetails():
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT isFilledApiDetails FROM UserData WHERE Email = %s", (session['email'],))
    result = cursor.fetchone()
    return result[0] is not None

def get_current_user_fernet_key():
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT Fernet_key FROM UserData WHERE Email = %s", (session['email'],))
    result = cursor.fetchone()
    return result[0] if result else None

@app.route("/connect_twitter", methods=["POST","GET"])
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
                return render_template("dashboard.html")
            else:
                session['canPost'] = False
                return redirect(url_for("dashboard"))
        else:
            return redirect(url_for("login"))
    if request.method == "GET":
        if session.get("email"):
            if check_user_exists(session['email']):
                    redirect(url_for("get_api_details"))
        else:
            return redirect(url_for("login"))

    return redirect(url_for("get_api_details"))

@app.route("/reset_api_details", methods=["POST"])
def reset_api_details():
    if request.method == "POST":
        if check_user_exists(session['email']):
            client_id = None
            client_secret = None
            twitter_access_token = None
            twitter_access_token_secret = None
            twitter_api_key = None
            twitter_api_secret = None
            screen_name = None
            isFilledApiDetails=False
            canPost=False

            UserData_conn = get_pg_connection()
            cursor = UserData_conn.cursor()
            cursor.execute("""
                           UPDATE UserData
                           SET twitter_api_key             = %s,
                               twitter_api_secret          = %s,
                               twitter_access_token        = %s,
                               twitter_access_token_secret = %s,
                               client_id                   = %s,
                               client_secret               = %s,
                               screen_name                 = %s
                           WHERE Email = %s""",
                           (twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_token_secret,
                            client_id, client_secret, screen_name, session['email']))
            cursor.close()
            UserData_conn.commit()

            UserData_conn = get_pg_connection()
            cursor = UserData_conn.cursor()
            cursor.execute("""
                           UPDATE UserData
                           SET isFilledApiDetails = %s,canPost = %s
                           WHERE Email = %s
                           """, (isFilledApiDetails, canPost, session['email']))
            cursor.close()
            UserData_conn.commit()
            return redirect(url_for("show_api_credentials"))
        else:
            return redirect(url_for("login"))
    return redirect(url_for("show_api_credentials"))


@app.route("/get_api_details")
def get_api_details():
    return render_template("get_api_details.html")


@app.route("/show_api_credentials"  )
def show_api_credentials():
    if session.get('email'):

        if check_user_exists(session['email']):

            UserData_conn = get_pg_connection()
            cursor = UserData_conn.cursor()
            cursor.execute("""
                           SELECT twitter_api_key,
                                  twitter_api_secret,
                                  twitter_access_token,
                                  twitter_access_token_secret,
                                  client_id,
                                  client_secret,
                                  screen_name,
                                  isFilledApiDetails,
                                  canPost
                           FROM UserData
                           WHERE Email = %s""",
                           (session['email'],))
            result = cursor.fetchone()
            twitter_api_key = result[0]
            twitter_api_secret = result[1]
            twitter_access_token = result[2]
            twitter_access_token_secret = result[3]
            client_id = result[4]
            client_secret = result[5]
            screen_name = result[6]
            isFilledApiDetails=result[7]
            canPost=result[8]

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
        return redirect(url_for("login"))

#logout
@app.route("/logout",methods=["POST"])
def logout():
    if request.method == "POST":
        if session.get('email'):
            if check_user_exists(session['email']):
                session.pop("username",None)
                session.pop("email",None)
                session.pop("toDashboard",False)
                session.clear()
                return redirect(url_for("login"))
        else:
            return redirect(url_for("login"))
    return redirect(url_for("dashboard"))




if __name__ == "__main__":

    app.run(debug=True)
