import tweepy
import os
from dotenv import load_dotenv
load_dotenv()

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

def post_tweet():
    """
    Handles a form submission to post a new tweet using OAuth 1.0a User Context.
    """
    tweet_text =  "Hello from my Flask app!"
    if not tweet_text:
        return "Tweet content is required", 400



    # Use the tweepy.Client with OAuth 1.0a User Context
    client = tweepy.Client(
        consumer_key= twitter_api_key,
        consumer_secret= twitter_api_secret,
        access_token= twitter_access_token,
        access_token_secret= twitter_access_token_secret
    )

    try:
        response = client.create_tweet(text=tweet_text)
        print("✅ Tweet posted successfully:", response.data)
        # Add success flash message here
    except Exception as e:
        print("❌ Error posting tweet:", e)
        # Add error flash message here

post_tweet()