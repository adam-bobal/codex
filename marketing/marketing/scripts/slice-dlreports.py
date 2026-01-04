import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By  # <--- ADD THIS LINE
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



# --- 1. UPDATE THESE VALUES ---
LOGIN_URL = "https://shop-accounts.slicelife.com/u/login/password?state=hKFo2SBrYnkzOFJxVGhjYlFmc2ZfUWlISkVwU1RuOWlLYWZaYaFur3VuaXZlcnNhbC1sb2dpbqN0aWTZIEtUazY0dllNUlNlYkZkNGdja284RTl5ekt6ZW55RHV3o2NpZNkgc2lMRUx3bDRDVDBoUDEwTkN3OU5MRHhXMXNEc25DZms"
ACCOUNTS_URL = "https://example.com/accounts/statements"
USERNAME = "BIGTIMEPIEGUYS@GMAIL.COM"
PASSWORD = "Papertowl1!"

# Use your browser's "Inspect" tool to find these selectors
USERNAME_FIELD_SELECTOR = (By.ID, "username") # Slice uses 'username' for the ID
PASSWORD_FIELD_SELECTOR = (By.ID, "password")
LOGIN_BUTTON_SELECTOR = (By.CSS_SELECTOR, "button[type='submit']")
DOWNLOAD_LINK_SELECTOR = (By.CSS_SELECTOR, "a.download-statement-link") # Placeholder
# --- END OF VALUES TO UPDATE ---

# --- CORRECTED SECTION ---
# Create a dedicated folder for downloads using a Path object
download_dir = Path("C:/users/aboba/projects/bookkeeping/slice")
download_dir.mkdir(exist_ok=True)

# Convert the Path object to an absolute string path for Selenium
absolute_download_dir = str(download_dir.resolve())

# Configure Chrome options to set the download directory
chrome_options = webdriver.ChromeOptions()
# Pass the STRING path to the preferences
prefs = {"download.default_directory": absolute_download_dir}
chrome_options.add_experimental_option("prefs", prefs)
# --- END OF CORRECTION ---

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20) # 20-second wait time

try:
    # --- Login ---
    print(f"Navigating to login page: {LOGIN_URL}")
    driver.get(LOGIN_URL)
    
    wait.until(EC.visibility_of_element_located(USERNAME_FIELD_SELECTOR)).send_keys(USERNAME)
    driver.find_element(*PASSWORD_FIELD_SELECTOR).send_keys(PASSWORD)
    driver.find_element(*LOGIN_BUTTON_SELECTOR).click()
    print("Login successful.")

    # --- Navigate and Download ---
    print(f"Navigating to accounts page: {ACCOUNTS_URL}")
    driver.get(ACCOUNTS_URL)
    
    # Wait for download links to be present on the page
    download_links = wait.until(EC.presence_of_all_elements_located(DOWNLOAD_LINK_SELECTOR))
    print(f"Found {len(download_links)} files to download.")

    for link in download_links:
        link.click()
        # A small pause to ensure the download is initiated
        time.sleep(1) 
        
    # --- Wait for Downloads to Complete ---
    print("Waiting for downloads to complete...")
    # Use the STRING path here as well for consistency
    while any(fname.endswith(".crdownload") for fname in os.listdir(absolute_download_dir)):
        time.sleep(1)

    print("All files downloaded successfully.")

finally:
    # Close the browser
    driver.quit()