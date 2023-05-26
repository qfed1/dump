import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import re
import csv
from bs4 import BeautifulSoup

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
driver.get('https://web.telegram.org/a/#-1746286357')

# Wait for the page to load
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'messages-container')))
except TimeoutException:
    print("Loading took too much time!")

# Open a CSV file to write the data
with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Href Links", "Bold Texts", "NBSP Texts"])  # Write the header

    # Get messages
    message_groups = driver.find_elements(By.XPATH, '//div[@class="message-date-group"]')

    # Extract data
    for group in message_groups:
        messages = group.find_elements(By.XPATH, './/div[starts-with(@class, "message")]')
        for message in messages:
            # Extract href links
            links = message.find_elements(By.XPATH, './/a[starts-with(@href, "https://etherscan.io/address/")]')
            href_links = [link.get_attribute('href') for link in links]

            # Extract text inside <strong> tags
            strong_texts = message.find_elements(By.XPATH, './/strong[@data-entity-type="MessageEntityBold"]')
            bold_texts = [strong_text.text for strong_text in strong_texts]

            # Get the inner HTML of the message
            inner_html = message.get_attribute('innerHTML')

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(inner_html, 'html.parser')

            # Find all text nodes containing '&nbsp;'
            nbsp_texts = [str(text) for text in soup.find_all(string=re.compile('&nbsp;'))]

            # Write the data into the CSV file
            writer.writerow([href_links, bold_texts, nbsp_texts])

# Close the driver
driver.quit()
