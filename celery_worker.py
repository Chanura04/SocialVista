
import os
import tweepy
from celery import Celery
from dotenv import load_dotenv
import requests
from requests_oauthlib import OAuth1Session
import json
load_dotenv()
from database import update_accountUpdatedOn_column,store_instant_cast_data,store_future_cast_data,store_instant_media_files
from zoneinfo import ZoneInfo
from datetime import datetime
from supabase import create_client
import tempfile
import os
from werkzeug.utils import secure_filename
import random

# Set up Celery. The broker is Redis, and the backend is for storing task results.
celery = Celery(
    "tasks",
    broker=os.environ.get("CELERY_BROKER_URL"),
    backend=os.environ.get("CELERY_RESULT_BACKEND")

)

@celery.task(bind=True)
def post_instant_tweet_task(self,email,platform_Name,tweet_text,reply_settings,decrypt_twitter_api_key,decrypt_twitter_api_secret,decrypt_twitter_user_access_token,decrypt_twitter_user_access_token_secret):
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

        sri_lanka_tz = ZoneInfo("Asia/Colombo")
        local_time = datetime.now(sri_lanka_tz)
        created_on = local_time.strftime("%Y-%m-%d %H:%M:%S")

        try:
            response = oauth.post(url, json=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            store_instant_cast_data(
                email,
                tweet_text,
                platform_Name,
                created_on,
                "Success"
            )
            # Print the API response
            print("Response status code:", response.status_code)
            json_response = response.json()
            print(json.dumps(json_response, indent=4))
        except tweepy.errors.TweepyException as e:

            error_msg = f"Twitter API Error: {e}"
            print(f"Twitter API Error: {e}")
            try:
                created_on = datetime.now(ZoneInfo("UTC"))
                store_instant_cast_data(
                    email,
                    tweet_text,
                    platform_Name,
                    created_on,
                    f"Failed: {str(e)}"
                )


            except Exception as db_error:

                print(f"Database storage warning: {db_error}")

            return {"status": "error", "message": error_msg}


        except Exception as e:

            print(f"Error posting tweet: {e}")

        return True
    except Exception as e:
        error_msg = f"Task initialization error: {e}"
        print(error_msg)
        return {"status": "error", "message": error_msg}



@celery.task(bind=True)
def post_future_tweet_task( self,email,need_to_publish, tweet_text,decrypt_twitter_api_key,decrypt_twitter_api_secret,decrypt_twitter_user_access_token,decrypt_twitter_user_access_token_secret,reply_settings):
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
        platform_name = "X"

        sri_lanka_tz = ZoneInfo("Asia/Colombo")

        local_time = datetime.now(sri_lanka_tz)
        created_on = local_time.strftime("%Y-%m-%d %H:%M:%S")
        status = "Success"
        store_future_cast_data(email, tweet_text, need_to_publish, platform_name, created_on, status)

        try:
            response = oauth.post(url, json=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Print the API response
            print("Response status code:", response.status_code)
            json_response = response.json()
            print(json.dumps(json_response, indent=4))



        except tweepy.errors.TweepyException as e:

            error_msg = f"Twitter API Error: {e}"
            print(f"Twitter API Error: {e}")
            try:
                created_on = datetime.now(ZoneInfo("UTC"))
                store_future_cast_data(email, tweet_text, need_to_publish, platform_name, created_on, f"Failed: {str(e)}")


            except Exception as db_error:

                print(f"Database storage warning: {db_error}")

            return {"status": "error", "message": error_msg}

        return True
    except Exception as e:
        error_msg = f"Task initialization error: {e}"
        print(error_msg)
        return {"status": "error", "message": error_msg}




@celery.task(bind=True)
def post_instant_media_task(
        self,
        email,
        tweet_text,
        file_content,  # ✅ Now receiving bytes instead of FileStorage
        original_filename,  # ✅ String
        content_type,  # ✅ String
        file_extension,
        decrypt_twitter_api_key,
        decrypt_twitter_api_secret,
        decrypt_twitter_user_access_token,
        decrypt_twitter_user_access_token_secret
):
    """
    A Celery task to post a tweet with media by uploading the file content directly.
    """
    try:
        # Initialize Twitter API clients
        auth_v1 = tweepy.OAuth1UserHandler(
            decrypt_twitter_api_key, decrypt_twitter_api_secret,
            decrypt_twitter_user_access_token, decrypt_twitter_user_access_token_secret
        )
        api = tweepy.API(auth_v1)

        client = tweepy.Client(
            consumer_key=decrypt_twitter_api_key,
            consumer_secret=decrypt_twitter_api_secret,
            access_token=decrypt_twitter_user_access_token,
            access_token_secret=decrypt_twitter_user_access_token_secret
        )

        # Upload to Supabase for backup/storage
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        supabase_filename = None

        if SUPABASE_URL and SUPABASE_KEY:
            try:
                supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

                # Generate random filename
                random_chars = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=3))
                random_num = random.randint(1, 10000)
                secure_original_filename = secure_filename(original_filename)
                extension = secure_original_filename.rsplit('.', 1)[-1].lower()
                supabase_filename = f"{random_chars}{random_num}.{extension}"




                # Upload to Supabase
                res = supabase_client.storage.from_("tweet-media").upload(
                    supabase_filename,
                    file_content,#Direct bytes upload
                    {"content-type": content_type}
                )

                if res.get("error"):
                    print(f"Supabase upload warning: {res['error']['message']}")
                else:
                    public_url = supabase_client.storage.from_("tweet-media").get_public_url(supabase_filename)
                    print(f"Backup stored at: {public_url}")

            except Exception as e:
                print(f"Supabase upload warning: {e}")
                # Continue with Twitter upload even if Supabase fails

        # Upload media to Twitter
        temp_file_path = None
        try:
            # Create temporary file for Twitter upload
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
                temp_file.write(file_content)  # ✅ Write bytes to temp file
                temp_file_path = temp_file.name

            # Upload using the temporary file path
            media_upload = api.media_upload(temp_file_path)
            media_id = media_upload.media_id
            print(f"Media uploaded to Twitter successfully. Media ID: {media_id}")


            # Create tweet with media
            response = client.create_tweet(
                text=tweet_text,
                media_ids=[media_id]
            )

            # Store record in database
            try:
                created_on = datetime.now(ZoneInfo("UTC"))
                store_instant_media_files(
                    email,
                    tweet_text,
                    file_content.filename,
                    file_content.content_type,
                    created_on,
                    "Success"
                )
                update_accountUpdatedOn_column(email)
            except Exception as db_error:
                print(f"Database storage warning: {db_error}")


            print("Tweet posted successfully!")
            print(json.dumps(response.data, indent=4))

        except tweepy.errors.TweepyException as e:
            error_msg = f"Twitter API Error: {e}"

            print(f"Twitter API Error: {e}")

            # Store failed attempt in database
            try:
                created_on = datetime.now(ZoneInfo("UTC"))
                store_instant_media_files(
                    email,
                    tweet_text,
                    file_content.filename,
                    file_content.content_type,
                    created_on,
                    f"Failed: {str(e)}"
                )
            except Exception as db_error:
                print(f"Database storage warning: {db_error}")
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"General Error: {e}"
            print(error_msg)
            return {"status": "error", "message": error_msg}

        finally:
                # Clean up temp file
                if temp_file_path and os.path.exists(temp_file_path):
                    try:
                        os.unlink(temp_file_path)
                        print("Temporary file cleaned up")
                    except Exception as cleanup_error:
                        print(f"Warning: Could not clean up temp file: {cleanup_error}")

    except Exception as e:
            error_msg = f"Task initialization error: {e}"
            print(error_msg)
            return {"status": "error", "message": error_msg}
