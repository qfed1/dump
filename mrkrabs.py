from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set path to chromedriver as per your configuration
webdriver_service = Service(ChromeDriverManager().install())

# Choose Chrome Browser
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)

# URL to open
url = "https://messages.google.com"

# Open the URL
driver.get(url)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

# Get the current URL
current_url = driver.current_url
print(f"Current URL: {current_url}")

# Check for URL changes
while True:
    if driver.current_url != current_url:
        print(f"URL changed: {driver.current_url}")
        current_url = driver.current_url

# Close the browser
driver.quit()
