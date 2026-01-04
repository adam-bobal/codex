function triggerResearch() {
  var sheet = SpreadsheetApp.getActiveSelection();
  var ticker = sheet.getValue();
  
  // PASTE YOUR NGROK URL HERE
  var apiUrl = "https://your-unique-id.ngrok-free.app/analyze"; 
  
  var options = {
    'method' : 'post',
    'contentType': 'application/json',
    'payload' : JSON.stringify({ "ticker": ticker })
  };

  var response = UrlFetchApp.fetch(apiUrl, options);
  var report = JSON.parse(response.getContentText()).analysis;
  sheet.offset(0, 1).setValue(report);
}