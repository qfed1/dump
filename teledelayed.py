import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
import random

# Initialize WebDriver
options = uc.ChromeOptions()

# Change the User-Agent
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

# Use a real browser profile
options.add_argument("user-data-dir=/path/to/your/profile")  # replace with the path to your profile

# You can add more options here if needed
options.add_argument('--disable-extensions')

driver = uc.Chrome(options=options)

# Navigate to the Telegram web client
driver.get('https://web.telegram.org/')

# Wait for user to manually log in
input("Press Enter after you have logged in...")

# List of channels
channels = ['https://web.telegram.org/a/#-1746286357', 'https://web.telegram.org/a/#-1234567890']  # Add your second channel URL here

# Initialize an empty DataFrame
df = pd.DataFrame()

for channel in channels:
    # Navigate to the channel using JavaScript
    driver.execute_script(f"window.location.href = '{channel}';")

    # Wait for the page to load
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'messages-container')))
    except TimeoutException:
        print("Loading took too much time!")

    # Get messages
    message_groups = driver.find_elements(By.XPATH, '//div[@class="message-date-group"]')

    # Extract and store messages
    for group in message_groups:
        messages = group.find_elements(By.XPATH, './/div[starts-with(@class, "message")]')
        for message in messages:
            # Split the message into elements and store each element in a separate column
            df = df.append(pd.Series(message.text.split()), ignore_index=True)

    # Add a random delay before switching to the next channel
    time.sleep(random.randint(5, 15))

# Close the driver
driver.quit()

# Write the DataFrame to a CSV file
df.to_csv('telegram_messages.csv', index=False)
