import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
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

# Navigate to the channel
driver.get('https://web.telegram.org/a/#5817029592')

# Wait for the page to load
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'messages-container')))
except TimeoutException:
    print("Loading took too much time!")

# Get messages
message_groups = driver.find_elements(By.XPATH, '//div[@class="message-date-group"]')

# Prepare the CSV file
messages_list = []

# Get messages and write them to the list
for group in message_groups:
    messages = group.find_elements(By.XPATH, './/div[starts-with(@class, "message")]')

    for message in messages:
        # Split the message text into subtexts and write each one to a new row
        subtexts = message.text.split()  # Replace the argument to split() with the appropriate delimiter
        messages_list.append(subtexts)

# Create DataFrame
df = pd.DataFrame(messages_list)

# Remove duplicate rows
df = df.drop_duplicates()

# Remove empty rows
df = df.dropna(how='all')

# Write to csv
df.to_csv('messagesvolume.csv', index=False, header=False)

# Close the driver
driver.quit()
