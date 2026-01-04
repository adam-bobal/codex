---
"""
Implementing an Exponential Backoff decorator is a hallmark of production-grade engineering. It ensures that transient issues—such as a 429 "Too Many Requests" error or a temporary network "hiccup"—don't cause your entire research pipeline to fail. Instead, the script "pauses" and retries with increasing delays.
1. The Exponential Backoff Decorator

This Python decorator can be placed above any function that calls an external API (Gemini, Perplexity, or Brave).

"""
---
import time
import random
import functools

def exponential_backoff(max_retries=5, base_delay=2):
    """
    Retries a function with an exponential wait time: 
    delay = base_delay * (2 ^ retry_count) + jitter
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Check for specific 'Retryable' errors (e.g., 429 or 503)
                    # For this example, we retry on all general exceptions
                    retries += 1
                    if retries == max_retries:
                        print(f"FAILED after {max_retries} attempts.")
                        raise e
                    
                    # Calculate delay with 'jitter' to prevent thundering herd
                    delay = (base_delay * (2 ** retries)) + random.uniform(0, 1)
                    print(f"Attempt {retries} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

2. Applying the Decorator to Your Research Pipeline

You can now wrap your API calls. This makes the logic cleaner and centralizes error management.
Python

@exponential_backoff(max_retries=3, base_delay=5)
def call_gemini_api(prompt):
    # Your existing Gemini client logic here
    # If this fails, the decorator will handle the retry automatically
    return client.models.generate_content(model="gemini-2.0-flash", contents=prompt)

def perform_deep_research(job: ResearchJob):
    try:
        # Step 1: Initialize sheet
        sheet = client.open_by_key(job.sheet_id).get_worksheet(0)
        
        # Step 2: Run protected AI call
        report = call_gemini_api(f"Analyze {job.ticker}...")
        
        # Step 3: Push to sheet
        sheet.update_acell(job.cell_address, report.text)
        
    except Exception as e:
        # Final reporting if backoff also fails
        sheet.update_acell(job.cell_address, f"❌
