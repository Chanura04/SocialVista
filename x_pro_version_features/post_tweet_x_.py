import requests
from requests_oauthlib import OAuth1Session
import json
import os
from dotenv import load_dotenv
load_dotenv()



#post tweet with loaction.get place id use
#https://developers.google.com/maps/documentation/javascript/place-id

# Your API credentials
consumer_key = os.getenv("TWITTER_API_KEY")
consumer_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Create an OAuth1Session object for authentication


# Your API credentials


# Create an OAuth1Session object
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)

# The X API endpoint for creating a tweet
url = "https://api.x.com/2/tweets"

# The JSON payload for the tweet with a geo tag
# IMPORTANT: You must have a valid place_id. This is for San Francisco, CA.
payload = {
    "text": "Hello from San Francisco! #SF",
    "geo": {
        "place_id": "df51dec6f4ee2b2c"
    }
}

# Send the POST request to the API
try:
    response = oauth.post(url, json=payload)
    response.raise_for_status() # Raises an HTTPError for bad responses

    # Print the API response
    print("Response status code:", response.status_code)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")