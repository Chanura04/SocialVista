
import os
import tweepy
from celery import Celery
from dotenv import load_dotenv
from flask import flash
from requests_oauthlib import OAuth1Session
import json
load_dotenv()

# Set up Celery. The broker is Redis, and the backend is for storing task results.
celery = Celery(
    "tasks",
    broker=os.environ.get("CELERY_BROKER_URL"),
    backend=os.environ.get("CELERY_RESULT_BACKEND")
)

@celery.task(bind=True)
def post_instant_tweet_task(self,email,tweet_text,reply_settings,decrypt_twitter_api_key,decrypt_twitter_api_secret,decrypt_twitter_user_access_token,decrypt_twitter_user_access_token_secret):
    """A Celery task to post an instant tweet for a user."""
    try:
        # The actual Twitter API call
        oauth = OAuth1Session(
            decrypt_twitter_api_key,
            client_secret=decrypt_twitter_api_secret,
            resource_owner_key=decrypt_twitter_user_access_token,
            resource_owner_secret=decrypt_twitter_user_access_token_secret,
        )
        url = "https://api.x.com/2/tweets"

        # The JSON payload for the tweet with reply settings
        # Options for 'reply_settings' are: 'mentionedUsers', 'following', 'everyone', 'verified'
        payload = {
            "text": tweet_text,
            "reply_settings": reply_settings
        }
        try:
            response = oauth.post(url, json=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Print the API response
            print("Response status code:", response.status_code)
            json_response = response.json()
            print(json.dumps(json_response, indent=4))


        except Exception as e:
            flash("Error posting tweet! Invalid API details...")
            print(f"Error posting tweet: {e}")

        return True
    except Exception as e:
        print(f"Error posting tweet for {email}: {e}")
        return False


@celery.task(bind=True)
def post_future_tweet_task( self,email, tweet_text,decrypt_twitter_api_key,decrypt_twitter_api_secret,decrypt_twitter_user_access_token,decrypt_twitter_user_access_token_secret,reply_settings):
    """A Celery task to post a scheduled tweet for a user."""
    try:
        # The actual Twitter API call
        oauth = OAuth1Session(
            decrypt_twitter_api_key,
            client_secret=decrypt_twitter_api_secret,
            resource_owner_key=decrypt_twitter_user_access_token,
            resource_owner_secret=decrypt_twitter_user_access_token_secret,
        )
        url = "https://api.x.com/2/tweets"

        # The JSON payload for the tweet with reply settings
        # Options for 'reply_settings' are: 'mentionedUsers', 'following', 'everyone', 'verified'
        payload = {
            "text": tweet_text,
            "reply_settings": reply_settings
        }
        try:
            response = oauth.post(url, json=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Print the API response
            print("Response status code:", response.status_code)
            json_response = response.json()
            print(json.dumps(json_response, indent=4))


        except Exception as e:
            flash("Error posting tweet! Invalid API details...")
            print(f"Error posting tweet: {e}")

        return True
    except Exception as e:
        print(f"Error posting tweet for {email}: {e}")
        return False