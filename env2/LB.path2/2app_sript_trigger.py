
"""
Matching Google Apps Script"

//Copy this into your Google Sheet (Extensions > Apps Script) to trigger the Python agent.

"""
JavaScript

function triggerResearch() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();
  const activeCell = sheet.getActiveCell();
  const ticker = activeCell.getValue();
  
  // Update with your current Ngrok URL
  const ngrokUrl = "https://your-unique-id.ngrok-free.app/research";
  
  const payload = {
    "ticker": ticker,
    "sheet_id": ss.getId(),
    "cell_address": activeCell.offset(0, 1).getA1Notation()
  };

  const options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload),
    "muteHttpExceptions": true
  };

  UrlFetchApp.fetch(ngrokUrl, options);
  activeCell.offset(0, 1).setValue("⏳ Processing Deep Analysis...");
}