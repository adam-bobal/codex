# Google Ads API Authentication Guide

## OAuth2 Flow Overview

Google Ads API uses **OAuth 2.0 for Web Server Applications** (3-legged OAuth).

## Prerequisites

1. **Google Cloud Project**
   - Create at: https://console.cloud.google.com
   - Enable Google Ads API

2. **Google Ads Developer Token**
   - Apply at: https://ads.google.com/aw/apicenter
   - Test account token available immediately
   - Production token requires review (2-5 days)

3. **OAuth2 Credentials**
   - Type: "Desktop app" or "Web application"
   - Download client_secrets.json

## Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Your App  │────▶│   Google    │────▶│  User Auth  │
│             │◀────│   OAuth2    │◀────│   Consent   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                                       │
       │         ┌─────────────┐              │
       └────────▶│ Access Token│◀─────────────┘
                 │ + Refresh   │
                 └─────────────┘
```

## Required OAuth2 Scopes

```python
SCOPES = ['https://www.googleapis.com/auth/adwords']
```

## Python Implementation

```python
# requirements: google-ads, google-auth-oauthlib

from google.ads.googleads.client import GoogleAdsClient
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

def authenticate_google_ads():
    """One-time OAuth2 flow, stores refresh token for future use."""
    
    # First-time auth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['https://www.googleapis.com/auth/adwords']
    )
    credentials = flow.run_local_server(port=8080)
    
    # Save credentials for reuse
    save_credentials(credentials)
    return credentials

def get_client():
    """Load saved credentials and create GoogleAdsClient."""
    
    config = {
        'developer_token': 'YOUR_DEVELOPER_TOKEN',
        'client_id': 'YOUR_CLIENT_ID',
        'client_secret': 'YOUR_CLIENT_SECRET',
        'refresh_token': 'YOUR_SAVED_REFRESH_TOKEN',
        'login_customer_id': 'YOUR_MCC_CUSTOMER_ID'  # optional
    }
    
    return GoogleAdsClient.load_from_dict(config)
```

## Config File Alternative (google-ads.yaml)

```yaml
developer_token: "YOUR_DEVELOPER_TOKEN"
client_id: "YOUR_CLIENT_ID.apps.googleusercontent.com"
client_secret: "YOUR_CLIENT_SECRET"
refresh_token: "YOUR_REFRESH_TOKEN"
login_customer_id: "1234567890"  # MCC ID if applicable
```

## Token Refresh

Refresh tokens are long-lived. The google-ads library handles automatic refresh.
Store refresh_token securely (encrypted file, environment variable, or secrets manager).

## Test Account Setup

1. Create test Google Ads account at ads.google.com
2. Use test developer token (no review needed)
3. All API calls work but don't affect real ads

## Production Checklist

- [ ] Apply for production developer token
- [ ] Complete Basic Access application
- [ ] Wait for approval (2-5 business days)
- [ ] Update token in config
