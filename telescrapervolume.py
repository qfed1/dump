import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import pandas as pd

# Initialize WebDriver
options = uc.ChromeOptions()

# You can add more options here if needed
options.add_argument('--disable-extensions')

driver = uc.Chrome(options=options)

# Navigate to the Telegram web client
driver.get('https://web.telegram.org/')

# Wait for user to manually log in
input("Press Enter after you have logged in...")

# Prompt user to manually navigate to the channel
input("Press Enter after you have navigated to the channel...")

# Wait for the page to load
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'messages-container')))
except TimeoutException:
    print("Loading took too much time!")

# Prepare the CSV file
messages_list = []

while True:
    # Get messages
    message_groups = driver.find_elements(By.XPATH, '//div[@class="message-date-group"]')

    for group in message_groups:
        messages = group.find_elements(By.XPATH, './/div[starts-with(@class, "message")]')
        for i in range(len(messages)):
            try:
                # Refresh the message reference
                message = group.find_elements(By.XPATH, './/div[starts-with(@class, "message")]')[i]
                # Split the message text into subtexts and write each one to a new row
                subtexts = message.text.split()  # Replace the argument to split() with the appropriate delimiter
                messages_list.append(subtexts)
            except StaleElementReferenceException:
                messages_list.append(["Error Reading Data"])

    # Create DataFrame
    df = pd.DataFrame(messages_list)

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Remove empty rows
    df = df.dropna(how='all')

    # Write to csv
    df.to_csv('messagesvolume.csv', index=False, header=False)

    # Wait for a while
    time.sleep(5)  # Adjust the sleep time as needed
