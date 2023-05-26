import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import sqlite3

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

# Connect to SQLite database
conn = sqlite3.connect('telegram_messages.db')
c = conn.cursor()

# Create table if it doesn't already exist
c.execute('''CREATE TABLE IF NOT EXISTS messages
             (message TEXT)''')

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
                subtexts = ' '.join(message.text.split())  # Replace the argument to split() with the appropriate delimiter
                c.execute("INSERT INTO messages VALUES (?)", (subtexts,))
            except StaleElementReferenceException:
                c.execute("INSERT INTO messages VALUES ('Error Reading Data')")

    # Commit the changes and wait for a while
    conn.commit()
    time.sleep(5)  # Adjust the sleep time as needed

# Close the connection when done
conn.close()
