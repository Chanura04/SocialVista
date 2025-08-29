

redirect_uri = "http://127.0.0.1:5000/"
import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()
# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.getenv("BEARER_TOKEN")
print(bearer_token)
#
# def create_url():
#     # Replace with user ID below
#     user_id = 1741051650247139329
#     return "https://api.twitter.com/2/users/{}/followers".format(user_id)


import requests
from requests_oauthlib import OAuth1Session
import json

# Your API credentials
consumer_key = os.getenv("TWITTER_API_KEY")
consumer_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Create an OAuth1Session object
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret,
)

# The X API endpoint for creating a tweet
url = "https://api.x.com/2/tweets"

# The JSON payload for the tweet with a poll
payload = {
    "text": "What's your favorite Python library for data analysis?",
    "poll": {
        "options": ["Pandas", "NumPy", "Matplotlib", "Scikit-learn"],
        "duration_minutes": 1440  # 24 hours
    }
}

# Send the POST request to the API
try:
    response = oauth.post(url, json=payload)
    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

    # Print the response from the API
    print("Response code:", response.status_code)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")