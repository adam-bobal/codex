import csv
import requests
import os
from datetime import datetime

# Environment variables (replace with your method of loading securely)
ACCESS_TOKEN = "YOUR_LONG_LIVED_ACCESS_TOKEN"
PAGE_ID = "YOUR_FACEBOOK_PAGE_ID"

GRAPH_URL = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"

def post_image_to_facebook(message, image_path):
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False

    with open(image_path, 'rb') as img_file:
        files = {"source": img_file}
        data = {
            "caption": message,
            "access_token": ACCESS_TOKEN
        }
        response = requests.post(GRAPH_URL, data=data, files=files)
        result = response.json()

        if "id" in result:
            print(f"✅ Posted successfully: {message}")
            return True
        else:
            print(f"❌ Failed to post: {result}")
            return False

def post_from_csv(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            message = row["message"]
            image_path = row["image_url"]
            post_image_to_facebook(message, image_path)
