import base64

import tweepy
import os
from dotenv import load_dotenv
load_dotenv()
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
import time
# Your client ID and secret should be stored securely
client_id = os.getenv("Client_ID")
client_secret = os.getenv("Client_Secret")
user_access_token=os.getenv("TWITTER_USER_ACCESS_TOKEN")
twitter_api_key=os.getenv("TWITTER_API_KEY")
twitter_api_secret=os.getenv("TWITTER_API_SECRET")
twitter_access_token=os.getenv("TWITTER_ACCESS_TOKEN")
twitter_access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
# This is the user's access token obtained from the authorization flow

user_access_token_secret = os.getenv("TWITTER_USER_ACCESS_TOKEN_SECRET")

# def post_tweet():
#     """
#     Handles a form submission to post a new tweet using OAuth 1.0a User Context.
#     """
#     tweet_text =  "Hello from my Flask app!"
#     if not tweet_text:
#         return "Tweet content is required", 400
#
#
#
#     # Use the tweepy.Client with OAuth 1.0a User Context
#     client = tweepy.Client(
#         consumer_key= twitter_api_key,
#         consumer_secret= twitter_api_secret,
#         access_token= twitter_access_token,
#         access_token_secret= twitter_access_token_secret
#     )
#
#     try:
#         response = client.create_tweet(text=tweet_text)
#         print("✅ Tweet posted successfully:", response.data)
#         # Add success flash message here
#     except Exception as e:
#         print("❌ Error posting tweet:", e)
#         # Add error flash message here
#
# post_tweet()



# from twikit import Client
# import asyncio
#
#
# async def get_tweets_with_twikit(username):
#     """
#     Asynchronously fetches a user's tweets using the twikit library.
#     """
#     client = Client('en-US')
#     tweets_data = []
#     try:
#         # These are coroutines, so they must be awaited
#         user = await client.get_user_by_screen_name(username)
#
#         # We use a loop to fetch multiple pages of tweets
#         async for tweet in user.get_tweets('Tweets'):
#             tweets_data.append({
#                 'id': tweet.id,
#                 'text': tweet.text,
#                 'author_name': tweet.user.name,
#                 'author_username': tweet.user.screen_name,
#                 'likes': tweet.favorite_count,
#                 'retweets': tweet.retweet_count,
#                 'created_at': tweet.created_at
#             })
#             # To get only the first 10-15 posts, you can break the loop here
#             if len(tweets_data) >= 15:
#                 break
#
#         return tweets_data
#
#     except Exception as e:
#         print(f"Error fetching tweets with twikit: {e}")
#         return []
#
#
# print(get_tweets_with_twikit("@__Chanura__"))


# from datetime import datetime
#
# local_time = datetime.now()
# print("Local time:", local_time.strftime("%H:%M:%S"))
# print("Date:", local_time.strftime("%Y-%m-%d "))

# from cryptography.fernet import Fernet
#
# class APIKeyHandler:
#
#     def __init__(self):
#         self.fernet_key = Fernet.generate_key()
#         self.cipher = Fernet(self.fernet_key)
#
#     def encrypt_key(self,key):
#         return self.cipher.encrypt(key.encode()).decode()
#     def decrypt_key(self,encrypted_key):
#         return self.cipher.decrypt(encrypted_key.encode()).decode()


# a=APIKeyHandler()
# print(a.encrypt_key("test"))
# print(a.decrypt_key("gAAAAABor9cLbQzEXdoSxQgoZkTMWJ2muMrEcKeQK8Ccpx3kp4veiVgKfQf7hHRABxDJWYXeD6G2q676JPWaYQyL532AQ0pLvg=="))
#
# a = APIKeyHandler()
# encrypted = a.encrypt_key("test")
# print("Encrypted:", encrypted)
# print("Decrypted:", a.decrypt_key(encrypted))

# from werkzeug.security import generate_password_hash,check_password_hash
#
# class Password:
#     def set_password(self,password):
#         self.password = generate_password_hash(password)
#         return self.password
#
#     def check_password(self,password):
#         return check_password_hash(self.password,password)
#
# a=Password()
# print(Password().set_password(password)("test"))
# print(a.check_password("test"))




# import psycopg2
#
#
# def get_pg_connection():
#     conn = psycopg2.connect(
#         host= os.getenv("DB_HOST"),
#         dbname=os.getenv("DB_NAME"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASSWORD"),
#         port=os.getenv("DB_PORT")
#
#
#     )
#
#     return conn
#
#
#
# def check_user_exists(email):
#     UserData_conn = get_pg_connection()
#     cursor = UserData_conn.cursor()
#     cursor.execute("SELECT 1 FROM UserData WHERE Email = %s ",(email,))
#     exists = cursor.fetchone()
#     return exists  is not None
#
# print(check_user_exists('chanurakarunanayake12@gmail.com'))






#get list id
# import requests
#
# bearer_token = os.getenv("BEARER_TOKEN")
# user_id = 1741051650247139329  # You can get this via /2/users/by/username/:username
#
# url = f"https://api.twitter.com/2/users/{user_id}/owned_lists"
# headers = {
#     "Authorization": f"Bearer {bearer_token}",
#     "User-Agent": "v2OwnedListsLookup"
# }
#
# response = requests.get(url, headers=headers)
# print(response.json())







#get user id
# import requests
#
# bearer_token = os.getenv("BEARER_TOKEN")
# username = "__Chanura__"  # Replace with your actual X handle (without @)
#
# url = f"https://api.twitter.com/2/users/by/username/{username}"
# headers = {
#     "Authorization": f"Bearer {bearer_token}",
#     "User-Agent": "v2UserLookup"
# }
#
# response = requests.get(url, headers=headers)
# user_data = response.json()
# print(user_data)
#
# # Extract user ID
# user_id = user_data.get("data", {}).get("id")
# print("Your user ID is:", user_id)

# (setup your client)

# from dotenv import load_dotenv
# load_dotenv()
# # Your API credentials
# consumer_key = os.getenv("TWITTER_API_KEY")
# consumer_secret = os.getenv("TWITTER_API_SECRET")
# access_token = os.getenv("TWITTER_ACCESS_TOKEN")
# access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
# user_id=1741051650247139329
# client = tweepy.Client(
#         consumer_key= twitter_api_key,
#         consumer_secret= twitter_api_secret,
#         access_token= twitter_access_token,
#         access_token_secret= twitter_access_token_secret
#     )
# # Get the user's timeline
# tweets = client.get_users_tweets(id=user_id)
#
# # Iterate through the tweets to get their IDs
# for tweet in tweets.data:
#     print(f"Tweet ID: {tweet.id}")
#     print(f"Tweet Text: {tweet.text}")
from zoneinfo import ZoneInfo
from datetime import datetime
sri_lanka_tz = ZoneInfo("Asia/Colombo")

# Current time in Sri Lanka
local_time = datetime.now(sri_lanka_tz)
created_on = local_time.strftime("%Y-%m-%d %H:%M:%S")
print(created_on)








