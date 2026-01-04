Implementation Workflow

    GCP Service Account: Create a service account in the Google Cloud Console, download the service_account.json, and share your Google Sheet with that account's email address.

    Start Python: Run python research_agent.py.

    Start Ngrok: Run ngrok http 8000.

    Connect: Update the ngrokUrl in your Apps Script with the forwarding address provided by Ngrok.

    Analyze: Type a ticker (e.g., AAPL) in a cell, select it, and run the script from the custom menu.