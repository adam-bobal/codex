---
project: marketing
type: Markdown
category: documentation
tags: automation, data, scripting
description: ```javascript
created: 2025-12-31T04:12:40.823193
---

#   This file contains the main functions that import data from CSV files into a Google Spreadsheet.
```javascript
// To learn more about this script, refer to the documentation: 
// https://developers.google.com/apps-script/samples/automations/import-csv-sheets

/*
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

/** 
 * This file contains the main functions that import data from CSV files into a Google Spreadsheet.
 */

// Application constants
const APP_TITLE = 'Trigger-driven CSV import [App Script Sample]'; // Application name
const APP_FOLDER = '[App Script sample] Import CSVs'; // Application primary folder
const SOURCE_FOLDER = 'Inbound CSV Files'; // Folder for the update files.
const PROCESSED_FOLDER = 'Processed CSV Files'; // Folder to hold processed files.
const SHEET_REPORT_NAME = 'Import CSVs'; // Name of destination spreadsheet.

// Application settings
const CSV_HEADER_EXIST = true;  // Set to true if CSV files have a header row, false if not.
const HANDLER_FUNCTION = 'updateApplicationSheet'; // Function called by installable trigger to run data processing.

/**
 * Installs a time-driven trigger that runs daily to import CSVs into the main application spreadsheet.
 * Prior to creating a new instance, removes any existing triggers to avoid duplication.
 * 
 * Called by setupSample() or run directly setting up the application.
 */
function installTrigger() {

  // Checks for an existing trigger to avoid creating duplicate instances.
  // Removes existing if found.
  const projectTriggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < projectTriggers.length; i++) {
    if (projectTriggers[i].getHandlerFunction() == HANDLER_FUNCTION) {
      console.log(`Existing trigger with Handler Function of '${HANDLER_FUNCTION}' removed.`);
      ScriptApp.deleteTrigger(projectTriggers[i]);
    }
  }
  // Creates the new trigger.
  let newTrigger = ScriptApp.newTrigger(HANDLER_FUNCTION)
    .timeBased()
    .atHour(23)   // Runs at 11 PM in the time zone of this script.
    .everyDays(1) // Runs once per day.
    .create();
  console.log(`New trigger with Handler Function of '${HANDLER_FUNCTION}' created.`);
}

/**
 * Handler function called by the trigger created with the "installTrigger" function.
 * Run this directly to execute the entire automation process of the application with a trigger.
 * 
 * Process: Iterates through CSV files located in the source folder (SOURCE_FOLDER),
 * and appends them to the end of destination spreadsheet (SHEET_REPORT_NAME).
 * Successfully processed CSV files are moved to the processed folder (PROCESSED_FOLDER) to avoid duplication.
 * Sends summary email with status of the import.
 */
function updateApplicationSheet() {

  // Gets application & supporting folders.
  const folderAppPrimary = getApplicationFolder_(APP_FOLDER);
  const folderSource = getFolder_(SOURCE_FOLDER);
  const folderProcessed = getFolder_(PROCESSED_FOLDER);

  // Gets the application's destination spreadsheet {Spreadsheet object}
  let objSpreadSheet = getSpreadSheet_(SHEET_REPORT_NAME, folderAppPrimary)

  // Creates arrays to track every CSV file, categorized as processed sucessfully or not.
  let filesProcessed = [];
  let filesNotProcessed = [];

  // Gets all CSV files found in the source folder.
  let cvsFiles = folderSource.getFilesByType(MimeType.CSV);

  // Iterates through each CSV file.
  while (cvsFiles.hasNext()) {

    let csvFile = cvsFiles.next();
    let isSuccess;

    // Appends the unprocessed CSV data into the Google Sheets spreadsheet.
    isSuccess = processCsv_(objSpreadSheet, csvFile);

    if (isSuccess) {
      // Moves the processed file to the processed folder to prevent future duplicate data imports.
      csvFile.moveTo(folderProcessed);
      // Logs the successfully processed file to the filesProcessed array.
      filesProcessed.push(csvFile.getName());
      console.log(`Successfully processed: ${csvFile.getName()}`);

    } else if (!isSuccess) {
      // Doesn't move the unsuccesfully processed file so that it can be corrected and reprocessed later.
      // Logs the unsuccessfully processed file to the filesNotProcessed array.
      filesNotProcessed.push(csvFile.getName());
      console.log(`Not processed: ${csvFile.getName()}`);
    }
  }
  
  // Prepares summary email.
  // Gets variables to link to this Apps Script project.
  const scriptId = ScriptApp.getScriptId();
  const scriptUrl = DriveApp.getFileById(scriptId).getUrl();
  const scriptName = DriveApp.getFileById(scriptId).getName();

  // Gets variables to link to the main application spreadsheet.
  const sheetUrl = objSpreadSheet.getUrl()
  const sheetName = objSpreadSheet.getName()   

  // Gets user email and timestamp.
  const emailTo = Session.getEffectiveUser().getEmail();
  const timestamp = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd HH:mm:ss zzzz");

  // Prepares lists and counts of processed CSV files.
  let processedList = "";
  const processedCount = filesProcessed.length
  for (const processed of filesProcessed) {
    processedList += processed + '<br>'
  };

  const unProcessedCount = filesNotProcessed.length
  let unProcessedList = "";
  for (const unProcessed of filesNotProcessed) {
    unProcessedList += unProcessed + '\n'
  };

  // Assembles email body as html.
  const eMailBody = `${APP_TITLE} ran an automated process at ${timestamp}.<br><br>` +
    `<b>Files successfully updated:</b> ${processedCount}<br>` +
    `${processedList}<br>` +
    `<b>Files not updated:</b> ${unProcessedCount}<br>` +
    `${unProcessedList}<br>` +
    `<br>View all updates in the Google Sheets spreadsheet ` +
    `<b><a href= "${sheetUrl}" target=\"_blank\">${sheetName}</a></b>.<br>` +
    `<br>*************<br>` +
    `<br>This email was generated by Google Apps Script. ` +
    `To learn more about this application or make changes, open the script project below: <br>` +
    `<a href= "${scriptUrl}" target=\"_blank\">${scriptName}</a>`

  MailApp.sendEmail({
    to: emailTo,
    subject: `Automated email from ${APP_TITLE}`,
    htmlBody: eMailBody
  });
  console.log(`Email sent to ${emailTo}`);
}

/**
 * Parses CSV data into an array and appends it after the last row in the destination spreadsheet.
 * 
 * @return {boolean} true if the update is successful, false if unexpected errors occur.
 */
function processCsv_(objSpreadSheet, csvFile) {

  try {
    // Gets the first sheet of the destination spreadsheet.
    let sheet = objSpreadSheet.getSheets()[0];

    // Parses CSV file into data array.
    let data = Utilities.parseCsv(csvFile.getBlob().getDataAsString());

    // Omits header row if application variable CSV_HEADER_EXIST is set to 'true'.
    if (CSV_HEADER_EXIST) {
      data.splice(0, 1);
    }
    // Gets the row and column coordinates for next available range in the spreadsheet. 
    let startRow = sheet.getLastRow() + 1;
    let startCol = 1;
    // Determines the incoming data size.
    let numRows = data.length;
    let numColumns = data[0].length;

    // Appends data into the sheet.
    sheet.getRange(startRow, startCol, numRows, numColumns).setValues(data);
    return true; // Success.

  } catch {
    return false; // Failure. Checks for CSV data file error.
  }
}
```
3 sampledata.gs 
```
/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/** 
 * This file contains functions to access headings and data for sample files.
 * 
 * Sample data is stored in the variable SAMPLE_DATA.
 */

// Fictitious sample data.
const SAMPLE_DATA = {
  "headings": [
    "PropertyName",
    "LeaseID",
    "LeaseLocation",
    "OwnerName",
    "SquareFootage",
    "RenewDate",
    "LastAmount",
    "LastPaymentDate",
    "Revenue"
  ],
  "csvFiles": [
    {
      "name": "Sample One.CSV",
      "rows": [
        {
          "PropertyName": "The Modern Building",
          "LeaseID": "271312",
          "LeaseLocation": "Mountain View CA 94045",
          "OwnerName": "Yuri",
          "SquareFootage": "17500",
          "RenewDate": "12/15/2022",
          "LastAmount": "100000",
          "LastPaymentDate": "3/01/2022",
          "Revenue": "12000"
        },
        {
          "PropertyName": "Garage @ 45",
          "LeaseID": "271320",
          "LeaseLocation": "Mountain View CA 94045",
          "OwnerName": "Luka",
          "SquareFootage": "1000",
          "RenewDate": "6/2/2022",
          "LastAmount": "50000",
          "LastPaymentDate": "4/01/2022",
          "Revenue": "20000"
        },
        {
          "PropertyName": "Office Park Deluxe",
          "LeaseID": "271301",
          "LeaseLocation": "Mountain View CA 94045",
          "OwnerName": "Sasha",
          "SquareFootage": "5000",
          "RenewDate": "6/2/2022",
          "LastAmount": "25000",
          "LastPaymentDate": "4/01/2022",
          "Revenue": "1200"
        }
      ]
    },
    {
      "name": "Sample Two.CSV",
      "rows": [
        {
          "PropertyName": "Tours Jumelles Minuscules",
          "LeaseID": "271260",
          "LeaseLocation": "8 Rue du Nom Fictif 341 Paris",
          "OwnerName": "Lucian",
          "SquareFootage": "1000000",
          "RenewDate": "7/14/2022",
          "LastAmount": "1250000",
          "LastPaymentDate": "5/01/2022",
          "Revenue": "77777"
        },
        {
          "PropertyName": "Barraca da Praia",
          "LeaseID": "271281",
          "LeaseLocation": "Avenida da Pastelaria 1903 Lisbon 1229-076",
          "OwnerName": "Raha",
          "SquareFootage": "1000",
          "RenewDate": "6/2/2022",
          "LastAmount": "50000",
          "LastPaymentDate": "4/01/2022",
          "Revenue": "20000"
        }
      ]
    },
    {
      "name": "Sample Three.CSV",
      "rows": [
        {
          "PropertyName": "Round Building in the Square",
          "LeaseID": "371260",
          "LeaseLocation": "8 Rue du Nom Fictif 341 Paris",
          "OwnerName": "Charlie",
          "SquareFootage": "75000",
          "RenewDate": "8/1/2022",
          "LastAmount": "250000",
          "LastPaymentDate": "6/01/2022",
          "Revenue": "22222"
        },
        {
          "PropertyName": "Square Building in the Round",
          "LeaseID": "371281",
          "LeaseLocation": "Avenida da Pastelaria 1903 Lisbon 1229-076",
          "OwnerName": "Lee",
          "SquareFootage": "10000",
          "RenewDate": "6/2/2022",
          "LastAmount": "5000",
          "LastPaymentDate": "4/01/2022",
          "Revenue": "1800"
        }
      ]
    }
  ]
}


/**
 * Returns headings for use in destination spreadsheet and CSV files.
 * @return {string[][]} array of each column heading as string.
 */
function getHeadings() {
  let headings = [[]];
  for (let i in SAMPLE_DATA.headings)
    headings[0].push(SAMPLE_DATA.headings[i]);
  return (headings)
}

/**
 * Returns CSV file names and content to create sample CSV files.
 * @return {object[]} {"file": ["name","csv"]}
 */
function getCSVFilesData() {

  let files = [];

  // Gets headings once - same for all files/rows.
  let csvHeadings = "";
  for (let i in SAMPLE_DATA.headings)
    csvHeadings += (SAMPLE_DATA.headings[i] + ',');

  // Gets data for each file by rows.
  for (let i in SAMPLE_DATA.csvFiles) {
    let sampleCSV = "";
    sampleCSV += csvHeadings;
    let fileName = SAMPLE_DATA.csvFiles[i].name
    for (let j in SAMPLE_DATA.csvFiles[i].rows) {
      sampleCSV += '\n'
      for (let k in SAMPLE_DATA.csvFiles[i].rows[j]) {
        sampleCSV += SAMPLE_DATA.csvFiles[i].rows[j][k] + ','
      }
    }
    files.push({ name: fileName, csv: sampleCSV })
  }
  return (files)
}

/*
 * Checks data functions are working as necessary.
 */
function test_getHeadings() {
  let h = getHeadings()
  console.log(h);
  console.log(h[0].length);
}

function test_getCSVFilesData() {
  const csvFiles = getCSVFilesData();
  console.log(csvFiles)

  for (const file of csvFiles) {
    console.log(file.name)
    console.log(file.csv)
  }
}
```
# setupsample.gs
```
/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/** 
 * This file contains functions that set up the folders and sample files used to demo the application.
 * 
 * Sample data for the application is stored in the SampleData.gs file.
 */

// Global variables for sample setup.
const INCLUDE_SAMPLE_DATA_FILES = true; // Set to true to create sample data files, false to skip.

/**
 * Runs the setup for the sample. 
 * 1) Creates the application folder and subfolders for unprocessed/processed CSV files.
 *    from global variables APP_FOLDER | SOURCE_FOLDER | PROCESSED_FOLDER
 * 2) Creates the sample Sheets spreadsheet in the application folder.
 *    from global variable SHEET_REPORT_NAME 
 * 3) Creates CSV files from sample data in the unprocessed files folder. 
 *    from variable SAMPLE_DATA in SampleData.gs.
 * 4) Creates an installable trigger to run process automatically at a specified time interval.
 */
function setupSample() {

  console.log(`Application setup for: ${APP_TITLE}`)

  // Creates application folder.
  const folderAppPrimary = getApplicationFolder_(APP_FOLDER);
  // Creates supporting folders.
  const folderSource = getFolder_(SOURCE_FOLDER);
  const folderProcessed = getFolder_(PROCESSED_FOLDER);

  console.log(`Application folders: ${folderAppPrimary.getName()}, ${folderSource.getName()}, ${folderProcessed.getName()}`)

  if (INCLUDE_SAMPLE_DATA_FILES) {

    // Sets up primary destination spreadsheet
    const sheet = setupPrimarySpreadsheet_(folderAppPrimary);

    // Gets the CSV files data - refer to the SampleData.gs file to view.
    const csvFiles = getCSVFilesData();

    // Processes each CSV file.
    for (const file of csvFiles) {
      // Creates CSV file in source folder if it doesn't exist.
      if (!fileExists_(file.name, folderSource)) {
        let csvFileId = DriveApp.createFile(file.name, file.csv, MimeType.CSV);
        console.log(`Created Sample CSV: ${file.name}`)
        csvFileId.moveTo(folderSource);
      }
    }
  }
  // Installs (or recreates) project trigger
  installTrigger()

  console.log(`Setup completed for: ${APP_TITLE}`)
}

/**
 * 
 */
function setupPrimarySpreadsheet_(folderAppPrimary) {

  // Creates the report destination spreadsheet if doesn't exist.
  if (!fileExists_(SHEET_REPORT_NAME, folderAppPrimary)) {

    // Creates new destination spreadsheet (report) with cell size of 20 x 10. 
    const sheet = SpreadsheetApp.create(SHEET_REPORT_NAME, 20, 10);

    // Adds the sample data headings.
    let sheetHeadings = getHeadings();
    sheet.getSheets()[0].getRange(1, 1, 1, sheetHeadings[0].length).setValues(sheetHeadings);
    SpreadsheetApp.flush();
    // Moves to primary application root folder.
    DriveApp.getFileById(sheet.getId()).moveTo(folderAppPrimary)

    console.log(`Created file: ${SHEET_REPORT_NAME} In folder: ${folderAppPrimary.getName()}.`)
    return sheet;
  }
}

/**
 * Moves sample content to Drive trash & uninstalls trigger.
 * This function removes all folders and content related to this application.
 */
function removeSample() {
  getApplicationFolder_(APP_FOLDER).setTrashed(true);
  console.log(`'${APP_FOLDER}' contents have been moved to Drive Trash folder.`)

  // Removes existing trigger if found.
  const projectTriggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < projectTriggers.length; i++) {
    if (projectTriggers[i].getHandlerFunction() == HANDLER_FUNCTION) {
      console.log(`Existing trigger with handler function of '${HANDLER_FUNCTION}' removed.`);
      ScriptApp.deleteTrigger(projectTriggers[i]);
    }
  }
}
  ```
# utilities

```
/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/** 
 * This file contains utility functions that work with application's folder and files.
 */

/**
 * Gets application destination spreadsheet from a given folder
 * Returns new sample version if orignal is not found. 
 * 
 * @param {string} fileName - Name of the file to test for.
 * @param {object} objFolder - Folder object in which to search.
 * @return {object} Spreadsheet object.
 */
function getSpreadSheet_(fileName, objFolder) {

  let files = objFolder.getFilesByName(fileName);

  while (files.hasNext()) {
    let file = files.next();
    let fileId = file.getId();

    const existingSpreadsheet = SpreadsheetApp.openById(fileId);
    return existingSpreadsheet;
  }

  // If application destination spreadsheet is missing, creates a new sample version.
  const folderAppPrimary = getApplicationFolder_(APP_FOLDER);
  const sampleSheet = setupPrimarySpreadsheet_(folderAppPrimary);
  return sampleSheet;
}

/**
 * Tests if a file exists within a given folder.
 * 
 * @param {string} fileName - Name of the file to test for.
 * @param {object} objFolder - Folder object in which to search.
 * @return {boolean} true if found in folder, false if not.
 */
function fileExists_(fileName, objFolder) {

  let files = objFolder.getFilesByName(fileName);

  while (files.hasNext()) {
    let file = files.next();
    console.log(`${file.getName()} already exists.`)
    return true;
  }
  return false;
}

/** 
 * Returns folder named in folderName parameter. 
 * Checks if folder already exists,  creates it if it doesn't.
 *
 * @param {string} folderName - Name of the Drive folder. 
 * @return {object} Google Drive Folder
 */
function getFolder_(folderName) {

  // Gets the primary folder for the application.
  const parentFolder = getApplicationFolder_();

  // Iterates subfolders to check if folder already exists.
  const subFolders = parentFolder.getFolders();
  while (subFolders.hasNext()) {
    let folder = subFolders.next();

    // Returns the existing folder if found.
    if (folder.getName() === folderName) {
      return folder;
    }
  }
  // Creates a new folder if one doesn't already exist.
  return parentFolder.createFolder(folderName)
    .setDescription(`Supporting folder created by ${APP_TITLE}.`);
}

/** 
 * Returns the primary folder as named by the APP_FOLDER variable in the Code.gs file.
 * Checks if folder already exists to avoid duplication.
 * Creates new instance if existing folder not found.
 *
 * @return {object} Google Drive Folder
 */
function getApplicationFolder_() {

  // Gets root folder, currently set to 'My Drive'
  const parentFolder = DriveApp.getRootFolder();

  // Iterates through the subfolders to check if folder already exists.
  const subFolders = parentFolder.getFolders();
  while (subFolders.hasNext()) {
    let folder = subFolders.next();

    // Returns the existing folder if found.
    if (folder.getName() === APP_FOLDER) {
      return folder;
    }
  }
  // Creates a new folder if one doesn't already exist.
  return parentFolder.createFolder(APP_FOLDER)
    .setDescription(`Main application folder created by ${APP_TITLE}.`);
}

/**
 * Tests getApplicationFolder_ and getFolder_
 * @logs details of created Google Drive folder.
 */
function test_getFolderByName() {

  let folder = getApplicationFolder_()
  console.log(`Name: ${folder.getName()}\rID: ${folder.getId()}\rURL:${folder.getUrl()}\rDescription: ${folder.getDescription()}`)
  // Uncomment the following to automatically delete test folder.
  // folder.setTrashed(true);

  folder = getFolder_(SOURCE_FOLDER);
  console.log(`Name: ${folder.getName()}\rID: ${folder.getId()}\rURL:${folder.getUrl()}\rDescription: ${folder.getDescription()}`)
  // Uncomment the following to automatically delete test folder.
  // folder.setTrashed(true);

  folder = getFolder_(PROCESSED_FOLDER);
  console.log(`Name: ${folder.getName()}\rID: ${folder.getId()}\rURL:${folder.getUrl()}\rDescription: ${folder.getDescription()}`)
  // Uncomment the following to automatically delete test folder.
  // folder.setTrashed(true);


}
```