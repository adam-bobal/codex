---
project: marketing
type: Markdown
category: documentation
tags: scripting
description: Here's a complete Python script section that **exchanges your short-lived token for a long-lived use
created: 2025-12-31T04:12:41.323666
---

Here's a complete Python script section that **exchanges your short-lived token for a long-lived user token** using Facebook's OAuth endpoint:

```python
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
```

---

### 📘 How it works

* Calls the `oauth/access_token` endpoint with your `APP_ID`, `APP_SECRET`, and `SHORT_TOKEN`.
* Returns a new long-lived token valid for approximately 60 days ([developers.facebook.com][1], [linkedin.com][2], [educative.io][3], [medium.com][4]).

---

### 🔧 Integration tip

Add this after `load_dotenv()` in your main script. You can store the result in `os.environ["LONG_TOKEN"]` or save it to your `.env` file if desired. Let me know if you'd like to automate refreshing or saving it!

[1]: https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived/?utm_source=chatgpt.com "Get Long-Lived Tokens - Facebook Login"
[2]: https://www.linkedin.com/pulse/using-facebook-sdk-python-package-unleash-power-tarik-aarbaoui?utm_source=chatgpt.com "Using the Facebook SDK Python Package to Unleash the Power of ..."
[3]: https://www.educative.io/courses/manage-profiles-pages-and-groups-using-facebook-graph-api/getting-short-lived-and-long-lived-access-tokens?utm_source=chatgpt.com "Getting Short-Lived and Long-Lived Access Tokens - Educative.io"
[4]: https://medium.com/nerd-for-tech/automate-facebook-posts-with-python-and-facebook-graph-api-858a03d2b142?utm_source=chatgpt.com "Automate Facebook Posts with Python and Facebook Graph API"
