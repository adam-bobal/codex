import requests

PAGE_ID = '115464798312582'
PAGE_ACCESS_TOKEN = 'EAAJDT6HZCIOEBPFLeLNIWjayVAomNcP9A0khb6pdyjZB1SlCynVvZAtjvZA2DXu1MiPZCS21ZC9GlFkSqrOxZB42oHON4yh4iZB1ss36ujfVB8XyQSG8poZABVOAt0HUfHaUwhCB1Mmab4AdIKi29MVAQZAuMo0FC1zVvz6QSIj9hNalUmb9Sat1NVtFyLJsLxfrRsW0eCefS52uyjDR75F7PXJ3w6MlR5F6fVPsUZD'

message = 'From now until close, best insult to the front counter staff gets 15% off'

url = f'https://graph.facebook.com/{PAGE_ID}/feed'
payload = {
    'message': message,
    'access_token': PAGE_ACCESS_TOKEN
}

response = requests.post(url, data=payload)
print(response.json())
