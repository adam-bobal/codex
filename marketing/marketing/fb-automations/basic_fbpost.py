import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
PAGE_ID = os.getenv("PAGE_ID")
PAGE_TOKEN = os.getenv("PAGE_TOKEN")

# Verify CSV location
csv_path = Path(__file__).parent / "daily_specials.csv"
if not csv_path.exists():
    raise FileNotFoundError(f"CSV not found at {csv_path}")

# Read today's special
import csv
with open(csv_path, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    today, special = next(reader)  # or appropriate logic
message = f"Today's special: {special}"

# Post to Facebook
url = f"https://graph.facebook.com/v23.0/{PAGE_ID}/feed"
payload = {"message": message, "access_token": PAGE_TOKEN}
response = requests.post(url, data=payload)

print(response.status_code, response.text)
response.raise_for_status()
print(f"✅ Posted successful – {response.json().get('id')}")
