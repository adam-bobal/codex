import csv
import requests
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# CONFIG
ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
PAGE_ID = os.getenv('PAGE_ID')

CSV_FILE = r'C:\Users\aboba\projects\fb-automations\data\waterice_specials.csv'

def post_to_facebook(message, image_url=None, link=None):
    if image_url:
        url = f'https://graph.facebook.com/v19.0/{PAGE_ID}/photos'
        payload = {
            'url': image_url,
            'caption': message,
            'access_token': ACCESS_TOKEN
        }
    else:
        url = f'https://graph.facebook.com/v19.0/{PAGE_ID}/feed'
        payload = {
            'message': message,
            'access_token': ACCESS_TOKEN
        }
        if link:
            payload['link'] = link

    response = requests.post(url, data=payload)
    return response.json()

def post_today_specials():
    today = datetime.datetime.now().strftime('%A')  # e.g., "Monday"
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        specials_posted = 0
        for row in reader:
            if row['day'].strip() == today:
                result = post_to_facebook(
                    message=row['message'],
                    image_url=row.get('image_url') or None,
                    link=row.get('link') or None
                )
                print(f"{row['type'].capitalize()} special posted: {result}")
                specials_posted += 1

        if specials_posted == 0:
            print(f"No specials found for {today}.")

if __name__ == '__main__':
    post_today_specials()
