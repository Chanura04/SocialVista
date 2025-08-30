import tweepy
import json
import os
from dotenv import load_dotenv
load_dotenv()
# Your API credentials
consumer_key = os.getenv("TWITTER_API_KEY")
consumer_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Your user ID
# user_id = 1741051650247139329



# Authenticate with the X API v2 client
client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# The ID of the tweet you want to look up
tweet_id = 1960285276389158993 # Replace with a valid tweet ID

# Get the tweet details
try:
    response = client.get_tweet(id=tweet_id)

    if response.data:
        tweet = response.data
        print("Tweet found successfully!")
        print("-----------------------")
        print(f"ID: {tweet.id}")
        print(f"Text: {tweet.text}")
    else:
        print("Tweet not found or an error occurred.")

except tweepy.errors.TweepyException as e:
    print(f"An error occurred: {e}")