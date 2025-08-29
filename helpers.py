# helpers.py

from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from flask import session
from database import get_pg_connection

class Password:
    def set_password(self, password):
        self.password = generate_password_hash(password)
        return self.password

    def check_password(self, hashed_password, plain_password):
        return check_password_hash(hashed_password, plain_password)

class APIKeyHandler:
    def __init__(self, fernet_key):
        self.fernet_key = fernet_key
        self.cipher = Fernet(self.fernet_key)

    def encrypt_key(self, key):
        return self.cipher.encrypt(key.encode()).decode()

    def decrypt_key(self, encrypted_key):
        return self.cipher.decrypt(encrypted_key.encode()).decode()

def get_current_user_fernet_key():
    conn = get_pg_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Fernet_key FROM UserData WHERE Email = %s", (session['email'],))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# def check_canPost():
#     conn = get_pg_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT canPost FROM UserData WHERE Email = %s", (session['email'],))
#     result = cursor.fetchone()
#     conn.close()
#     return result[0] is not None
#
# def check_api_details():
#     conn = get_pg_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT twitter_api_key,twitter_api_secret FROM UserData WHERE Email = %s", (session['email'],))
#     result = cursor.fetchone()
#     conn.close()
#     return result[0] is not None and result[1] is not None