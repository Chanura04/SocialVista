# database.py
from flask import session
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
from zoneinfo import ZoneInfo
import logging
def get_pg_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    return conn

def get_user_password(email):
    # ... your function logic here
    conn = get_pg_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM UserData WHERE email = %s", (email,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_first_name(email):
    # ... your function logic here
    conn = get_pg_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name FROM UserData WHERE email = %s", (email,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
def check_user_exists(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT 1 FROM UserData WHERE email = %s ",(email,))
    exists = cursor.fetchone()
    return exists is not None


def add_new_user(first_name, last_name, email, encrypt_password, fernet_key_str,referralCode,account_status):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("INSERT INTO UserData (first_name, last_name, email, password, fernet_key,referralCode,account_status) VALUES (%s,%s,%s,%s,%s,%s,%s)",(first_name, last_name, email, encrypt_password, fernet_key_str,referralCode,account_status))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()

def update_accountUpdatedOn_column(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    sri_lanka_tz = ZoneInfo("Asia/Colombo")
    local_time = datetime.now(sri_lanka_tz)
    updated_on = local_time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE UserData SET account_updated_on= %s WHERE email = %s", (updated_on,email))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()

def update_accountCreatedOn_column(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    local_time = datetime.now()
    cursor.execute("UPDATE UserData SET account_created_on= %s WHERE email = %s", (local_time.strftime("%Y-%m-%d %H:%M:%S"),email))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()


def check_api_details():
    # user = User.query.filter_by(email=session['email']).first()
    if check_user_exists(session['email']):

        UserData_conn = get_pg_connection()
        cursor = UserData_conn.cursor()
        cursor.execute("SELECT twitter_api_key,twitter_api_secret,twitter_access_token,twitter_access_token_secret,client_id,client_secret,screen_name FROM x_api_details WHERE email = %s", (session['email'],))
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

def check_canPost():
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT canPost FROM x_api_details WHERE email = %s", (session['email'],))
    result = cursor.fetchone()
    return result[0] is not None

def get_user_role(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT role FROM UserData WHERE email = %s", (email,))
    result = cursor.fetchone()
    return result[0] if result else 'user'


def store_future_cast_data(email,context,Need_to_Publish,Platform_Name,Created_on,Status):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("INSERT INTO FutureCastData (email,context,need_to_publish,platform_name,created_on,status) VALUES (%s,%s,%s,%s,%s,%s)",(email,context,Need_to_Publish,Platform_Name,Created_on,Status))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()


def get_stored_future_cast_data(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT (context,need_to_publish,platform_name,status) FROM FutureCastData WHERE email = %s", (email,))
    result = cursor.fetchall()
    return result
def get_stored_future_cast_media_data(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT (context,need_to_publish,platform_name,status) FROM FutureCastMediaData WHERE email = %s", (email,))
    result = cursor.fetchall()
    return result
def store_future_cast_Media_data(email,context,Need_to_Publish,Platform_Name,file_name,file_type,Created_on,Status):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("INSERT INTO FutureCastMediaData (email,context,need_to_publish,platform_name,file_name,file_type,created_on,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(email,context,Need_to_Publish,Platform_Name,file_name,file_type,Created_on,Status))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()

def store_instant_cast_data(email,context,Platform_Name,Created_on,Status):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("INSERT INTO InstantCastData (email,context,platform_name,created_on,status) VALUES (%s,%s,%s,%s,%s)",(email,context,Platform_Name,Created_on,Status))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()

def get_stored_instant_cast_data(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT (context,platform_name,status) FROM InstantCastData WHERE email = %s", (email,))
    result = cursor.fetchall()
    return result
def get_pg_connections():
    """Establishes a connection to the PostgreSQL database using environment variables."""
    try:
        connection_string = os.environ.get("DATABASE_URL")
        conn = psycopg2.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
    UserData_conn.close()

def store_instant_media_files(email,context,file_name,file_path,Created_on,Status):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("INSERT INTO InstantMediaFiles (email,context,file_name,file_path,created_on,status) VALUES (%s,%s,%s,%s,%s,%s)",(email,context,file_name,file_path,Created_on,Status))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()
def get_stored_instant_media_files(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT (context,file_name,status) FROM InstantMediaFiles WHERE email = %s", (email,))
    result = cursor.fetchall()
    return result
def get_api_details(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT twitter_api_key,twitter_api_secret,twitter_access_token,twitter_access_token_secret,client_id,client_secret,screen_name FROM x_api_details WHERE email = %s", (email,))
    result = cursor.fetchone()
    return result

def update_api_details_staus(canPost,isFilledApiDetails,email) :
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("""
                   UPDATE x_api_details
                   SET isFilledApiDetails = %s,
                       canPost            = %s
                   WHERE email = %s
                   """, (isFilledApiDetails, canPost, email))
    cursor.close()
    UserData_conn.commit()

def add_X_api_details(email,encrypted_twitter_api_key,
                                            encrypted_twitter_api_secret,
                                            encrypted_twitter_access_token,
                                            encrypted_twitter_access_token_secret,
                                            encrypted_client_id,
                                            encrypted_client_secret,
                                            encrypted_screen_name,
                                            isFilledApiDetails,
                                            canPost):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute(
        """
        INSERT INTO x_api_details
         (
             email,
             twitter_api_key,      
             twitter_api_secret,
             twitter_access_token ,
             twitter_access_token_secret ,
             client_id,
             client_secret,
             screen_name,
             isFilledApiDetails,
             canPost
         )
       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            email,
            encrypted_twitter_api_key,
            encrypted_twitter_api_secret,
            encrypted_twitter_access_token,
            encrypted_twitter_access_token_secret,
            encrypted_client_id,
            encrypted_client_secret,
            encrypted_screen_name,
            isFilledApiDetails,
            canPost
            )
    )
    cursor.close()
    UserData_conn.commit()

def reset_api_details_db(email):

    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()

    cursor.execute("""DELETE FROM x_api_details WHERE email = %s""", (email,))
    logging.info("reset_api_details")
    cursor.close()
    UserData_conn.commit()
    cursor.close()
    UserData_conn.commit()


def show_api_credentials_db(email):
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
                   FROM x_api_details
                   WHERE email = %s""",
                   (email,))
    result = cursor.fetchone()
    twitter_api_key = result[0]
    twitter_api_secret = result[1]
    twitter_access_token = result[2]
    twitter_access_token_secret = result[3]
    client_id = result[4]
    client_secret = result[5]
    screen_name = result[6]
    isFilledApiDetails = result[7]
    canPost = result[8]
    return [twitter_api_key,twitter_api_secret,twitter_access_token,twitter_access_token_secret,client_id,client_secret,screen_name,isFilledApiDetails,canPost]


def add_referral_code_used_users(owner_email, referred_user_email, referralCode):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("INSERT INTO track_referralCode (owner_email,referred_user_email,referralCode) VALUES (%s,%s,%s)", (owner_email, referred_user_email, referralCode))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()

def get_referral_code_owner(referralCode):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT email FROM userdata WHERE referralCode = %s", (referralCode,))
    result = cursor.fetchone()
    return result[0] if result else None


def track_referralCode(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT count(referralCode) FROM track_referralCode WHERE owner_email = %s", (email,))
    result = cursor.fetchone()
    print(result)
    result=int(result[0])
    if result==3:
        return True
    else:
        return False

def update_user_role(email,role):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("UPDATE UserData SET role = %s WHERE email = %s", (role,email))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()


def get_currentUser_referred_count(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT count(referralCode) FROM track_referralCode WHERE owner_email = %s", (email,))

    referral_count=cursor.fetchone()
    result=int(referral_count[0])

    print("check in db",email)
    return result

def get_is_filled_api_details(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT isFilledApiDetails FROM x_api_details WHERE email = %s  ", (email,))
    result = cursor.fetchone()
    return result[0] if result else None