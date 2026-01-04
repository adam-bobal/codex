import requests

# ACCESS CREDENTIALS - NEEDED TO ACCESS THE SITE
PAGE_ID             = '115464798312582'
PAGE_ACCESS_TOKEN   = 'EAAJDT6HZCIOEBPFLeLNIWjayVAomNcP9A0khb6pdyjZB1SlCynVvZAtjvZA2DXu1MiPZCS21ZC9GlFkSqrOxZB42oHON4yh4iZB1ss36ujfVB8XyQSG8poZABVOAt0HUfHaUwhCB1Mmab4AdIKi29MVAQZAuMo0FC1zVvz6QSIj9hNalUmb9Sat1NVtFyLJsLxfrRsW0eCefS52uyjDR75F7PXJ3w6MlR5F6fVPsUZD'

# USE r"path\to\file" with \ -> corrected an error
IMAGE_PATH = r"C:\Users\aboba\projects\fb-automations\images\waterice_dailyflavor\thur_rainbow.png"
MESSAGE = f''            = 'From now until close, best insult to the front counter staff gets 15% off'


# Use the /photos edge to upload a file
url = f'https://graph.facebook.com/v19.0/{PAGE_ID}/photos'

files = {
    'source': open(IMAGE_PATH, 'rb')        # binary image data :contentReference[oaicite:2]{index=2}
}
data = {
    'caption': message,                      # post text
    'access_token': PAGE_ACCESS_TOKEN        # your Page Access Token
}

response = requests.post(url, files=files, data=data)
print(response.json())
