from dotenv import load_dotenv
import os

load_dotenv()
print("page_token")
print(os.getenv("PAGE_TOKEN"))  # Loads directly from .env
print("page_id")
print(os.getenv("PAGE_ID"))

