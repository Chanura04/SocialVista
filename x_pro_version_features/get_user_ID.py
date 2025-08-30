# # Extract user ID
import requests
from dotenv import load_dotenv
load_dotenv()
import os
bearer_token = os.getenv("BEARER_TOKEN")
username = "__Chanura__"  # Replace with your actual X handle (without @)

url = f"https://api.twitter.com/2/users/by/username/{username}"
headers = {
    "Authorization": f"Bearer {bearer_token}",
    "User-Agent": "v2UserLookup"
}

response = requests.get(url, headers=headers)
user_data = response.json()
print(user_data)

# Extract user ID
user_id = user_data.get("data", {}).get("id")
print("Your user ID is:", user_id)
