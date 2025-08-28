import tweepy
import os
from dotenv import load_dotenv
load_dotenv()
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
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



from twikit import Client
import asyncio


async def get_tweets_with_twikit(username):
    """
    Asynchronously fetches a user's tweets using the twikit library.
    """
    client = Client('en-US')
    tweets_data = []
    try:
        # These are coroutines, so they must be awaited
        user = await client.get_user_by_screen_name(username)

        # We use a loop to fetch multiple pages of tweets
        async for tweet in user.get_tweets('Tweets'):
            tweets_data.append({
                'id': tweet.id,
                'text': tweet.text,
                'author_name': tweet.user.name,
                'author_username': tweet.user.screen_name,
                'likes': tweet.favorite_count,
                'retweets': tweet.retweet_count,
                'created_at': tweet.created_at
            })
            # To get only the first 10-15 posts, you can break the loop here
            if len(tweets_data) >= 15:
                break

        return tweets_data

    except Exception as e:
        print(f"Error fetching tweets with twikit: {e}")
        return []


print(get_tweets_with_twikit("@__Chanura__"))