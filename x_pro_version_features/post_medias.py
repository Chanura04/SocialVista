#can add photos and videos


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

# V1.1 API for media upload
auth_v1 = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret,
    access_token, access_token_secret
)
api = tweepy.API(auth_v1)

# V2 API for tweet creation
client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

# Step 1: Upload media (replace with your file)
try:
    media_upload = api.media_upload("C:/Udemy/Github Projects/SocialVista/x_pro_version_features/video.mp4")
    media_id = media_upload.media_id
    print(f"Media uploaded successfully. Media ID: {media_id}")
except tweepy.errors.TweepyException as e:
    print(f"Error uploading media: {e}")
    media_id = None

# Step 2: Create the tweet with the media and a user tag
if media_id:
    tweet_text = "Check out this image! Tagging my friend @example_user"
    try:
        response = client.create_tweet(
            text=tweet_text,
            media_ids=[media_id]
        )
        print("Tweet posted successfully!")
        print(json.dumps(response.data, indent=4))
    except tweepy.errors.TweepyException as e:
        print(f"Error creating tweet: {e}")