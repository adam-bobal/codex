"""
Updated Python Background Task with Error Handling

This refined function includes specific error handling for gspread (the sheet connection)

"""

import traceback
import gspread
from google.api_core import exceptions as google_exceptions

def perform_deep_research(job: ResearchJob):
    """
    Orchestrates the research with deep error handling and 
    reports progress/failures back to Google Sheets.
    """
    try:
        # 1. Initialize Sheet Connection
        sheet = client.open_by_key(job.sheet_id).get_worksheet(0)
        
        # 2. Run the Analysis (Gemini/Perplexity/Brave logic)
        # Note: We wrap the actual 'brain' logic in its own try/except for granularity
        try:
            report = run_automated_research(job.ticker)
        except google_exceptions.ResourceExhausted:
            report = "❌ Error: API Quota exceeded. Please try again in 60 seconds."
        except Exception as ai_err:
            report = f"❌ AI Analysis Error: {str(ai_err)}"

        # 3. Final Push to Sheet
        sheet.update_acell(job.cell_address, report)

    except gspread.exceptions.APIError as g_err:
        print(f"Permanent Sheet Error: {g_err}")
    except Exception as e:
        # 4. Critical Catch-All: Report the traceback to the sheet so you can debug
        error_detailed = f"❌ Critical System Error: {str(e)}\n\nTraceback: {traceback.format_exc()[:200]}..."
        try:
            # Attempt to write the error to the sheet one last time
            sheet.update_acell(job.cell_address, error_detailed)
        except:
            # If we can't even write to the sheet, log to the local terminal
            print(f"Fatal error: Could not write to sheet. {str(e)}")

