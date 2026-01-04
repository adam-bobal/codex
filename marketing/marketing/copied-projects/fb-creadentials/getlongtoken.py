import os
import requests

# Load environment variables
SHORT_TOKEN = os.getenv("SHORT_TOKEN")
APP_ID      = os.getenv("APP_ID")
APP_SECRET  = os.getenv("APP_SECRET")

# Exchange for long-lived token
response = requests.get(
    "https://graph.facebook.com/v23.0/oauth/access_token",
    params={
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": SHORT_TOKEN
    }
)
response.raise_for_status()
data = response.json()

LONG_TOKEN = data.get("access_token")
expires_in = data.get("expires_in")

print(f"✅ LONG_TOKEN: {LONG_TOKEN}")
print(f"Expires in (seconds): {expires_in} (≈{int(expires_in/86400)} days)")
