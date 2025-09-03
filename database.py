# database.py
from flask import session
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
from zoneinfo import ZoneInfo

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
    cursor.execute("SELECT Password FROM UserData WHERE Email = %s", (email,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_first_name(email):
    # ... your function logic here
    conn = get_pg_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT FirstName FROM UserData WHERE Email = %s", (email,))
    result = cursor.fetchone()
    conn.close()
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
    sri_lanka_tz = ZoneInfo("Asia/Colombo")
    local_time = datetime.now(sri_lanka_tz)
    updated_on = local_time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE UserData SET account_updated_on= %s WHERE Email = %s", (updated_on,email))
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

def check_canPost():
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT canPost FROM UserData WHERE Email = %s", (session['email'],))
    result = cursor.fetchone()
    return result[0] is not None

def get_user_role(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT role FROM UserData WHERE Email = %s", (email,))
    result = cursor.fetchone()
    return result[0] if result else 'user'


def store_future_cast_data(email,context,Need_to_Publish,Platform_Name,Created_on,Status):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("INSERT INTO FutureCastData (Email,Context,Need_to_Publish,Platform_Name,Created_on,Status) VALUES (%s,%s,%s,%s,%s,%s)",(email,context,Need_to_Publish,Platform_Name,Created_on,Status))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()


def store_future_cast_Media_data(email,context,Need_to_Publish,Platform_Name,file_name,file_type,Created_on,Status):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("INSERT INTO FutureCastMediaData (Email,Context,Need_to_Publish,Platform_Name,file_name,file_type,Created_on,,Created_on,Status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(email,context,Need_to_Publish,Platform_Name,file_name,file_type,Created_on,Status))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()

def store_instant_cast_data(email,context,Platform_Name,Created_on,Status):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("INSERT INTO InstantCastData (Email,Context,Platform_Name,Created_on,Status) VALUES (%s,%s,%s,%s,%s)",(email,context,Platform_Name,Created_on,Status))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()

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
    cursor.execute("INSERT INTO InstantMediaFiles (Email,Context,File_Name,File_Path,Created_on,Status) VALUES (%s,%s,%s,%s,%s,%s)",(email,context,file_name,file_path,Created_on,Status))
    UserData_conn.commit()
    cursor.close()
    UserData_conn.close()

def get_api_details(email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("SELECT twitter_api_key,twitter_api_secret,twitter_access_token,twitter_access_token_secret,client_id,client_secret,screen_name FROM UserData WHERE Email = %s", (email,))
    result = cursor.fetchone()
    return result

def update_api_details_staus(canPost,isFilledApiDetails,email) :
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute("""
                   UPDATE UserData
                   SET isFilledApiDetails = %s,
                       canPost            = %s
                   WHERE Email = %s
                   """, (isFilledApiDetails, canPost, email))
    cursor.close()
    UserData_conn.commit()

def add_X_api_details(encrypted_twitter_api_key,
                                            encrypted_twitter_api_secret,
                                            encrypted_twitter_access_token,
                                            encrypted_twitter_access_token_secret,
                                            encrypted_client_id,
                                            encrypted_client_secret,
                                            encrypted_screen_name,
                                            email):
    UserData_conn = get_pg_connection()
    cursor = UserData_conn.cursor()
    cursor.execute(
        """
        UPDATE UserData
        SET twitter_api_key             = %s,
            twitter_api_secret          = %s,
            twitter_access_token        = %s,
            twitter_access_token_secret = %s,
            client_id                   = %s,
            client_secret               = %s,
            screen_name                 = %s
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
            email)
    )
    cursor.close()
    UserData_conn.commit()