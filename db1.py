import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import sqlite3

# Initialize WebDriver
options = uc.ChromeOptions()
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

# Prepare the database
conn = sqlite3.connect('messages.db')  # Create a database named messages.db
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS messages (message_text TEXT PRIMARY KEY)''')  # Create a table if it doesn't exist

# Load existing messages into Python set
cursor.execute('''SELECT message_text FROM messages''')
existing_messages = {row[0] for row in cursor.fetchall()}

while True:
    # Get messages
    message_groups = driver.find_elements(By.XPATH, '//div[@class="message-date-group"]')

    for group in message_groups:
        try:
            messages = group.find_elements(By.XPATH, './/div[starts-with(@class, "message")]')
            for i in range(len(messages)):
                try:
                    # Refresh the message reference
                    message = group.find_elements(By.XPATH, './/div[starts-with(@class, "message")]')[i]
                    # Join the message text into one string and check if it's already in the database
                    full_message = ' '.join(message.text.split())
                    if full_message not in existing_messages:
                        cursor.execute('''INSERT OR IGNORE INTO messages VALUES (?)''', (full_message,))  # Insert message into the table
                        existing_messages.add(full_message)  # Add the new message to the set
                except StaleElementReferenceException:
                    cursor.execute('''INSERT OR IGNORE INTO messages VALUES (?)''', ("Error Reading Data",))  # Insert error message
                except IndexError:
                    # Index out of range error occurred, move on to the next message group
                    break
        except StaleElementReferenceException:
            continue  # If StaleElementReferenceException, continue to next iteration

    # Commit the changes
    conn.commit()

    # Wait for a while
    time.sleep(5)  # Adjust the sleep time as needed
