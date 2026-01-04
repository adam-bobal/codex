"""
1. Unified Python Research Agent (research_agent.py)

This script handles the heavy lifting. Ensure you have your service_account.json and API keys ready.
"""---

import os
import time
import random
import functools
import traceback
import asyncio
import gspread
from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks
from oauth2client.service_account import ServiceAccountCredentials
from google import genai
from google.api_core import exceptions as google_exceptions

# --- 1. CONFIGURATION & MODELS ---
app = FastAPI()

class ResearchJob(BaseModel):
    ticker: str
    sheet_id: str
    cell_address: str

# API Keys (Ideally loaded from .env)
GEMINI_API_KEY = "YOUR_GEMINI_KEY"
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# --- 2. THE BULLETPROOF DECORATOR ---
def exponential_backoff(max_retries=5, base_delay=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise e
                    delay = (base_delay * (2 ** retries)) + random.uniform(0, 1)
                    print(f"Attempt {retries} failed. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

# --- 3. CORE ANALYTICS ENGINE ---
@exponential_backoff(max_retries=3, base_delay=4)
def run_automated_research(ticker: str):
    """Simulates the Gemini + Perplexity + Brave orchestration logic."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Example Prompt incorporating financial metrics
    prompt = f"""
    Perform a high-level financial analysis for {ticker}.
    1. Calculate the 3-year Revenue CAGR: $CAGR = \\left(\\frac{EV}{BV}\\right)^{\\frac{1}{n}} - 1$.
    2. Assess current valuation multiples (P/E, EV/EBITDA) against sector medians.
    3. Identify three critical risks from the latest 10-K filing.
    """
    
    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text

# """--- 4. ASYNCHRONOUS BACKGROUND TASK ---"""

def perform_deep_research_task(job: ResearchJob):
    try:
        # Authenticate with Google Sheets
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPE)
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(job.sheet_id).get_worksheet(0)

        # Execute Analysis
        report = run_automated_research(job.ticker)

        # Push to Sheet
        sheet.update_acell(job.cell_address, report)

    except google_exceptions.ResourceExhausted:
        error_msg = "❌ Error: Gemini API rate limit exceeded."
        sheet.update_acell(job.cell_address, error_msg)
    except Exception as e:
        error_msg = f"❌ Critical Error: {str(e)}\n{traceback.format_exc()[:100]}"
        sheet.update_acell(job.cell_address, error_msg)

# --- 5. API ENDPOINTS ---
@app.post("/research")
async def start_research(job: ResearchJob, background_tasks: BackgroundTasks):
    background_tasks.add_task(perform_deep_research_task, job)
    return {"status": "Analysis initiated. Results will appear in your sheet shortly."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)