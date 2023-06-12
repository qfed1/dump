from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pyperclip
import aiosqlite
import asyncio

def get_contract_source(address):
    # Setup webdriver
    webdriver_service = Service('/usr/local/bin/chromedriver')
    driver = webdriver.Chrome(service=webdriver_service)

    url = f'https://etherscan.io/address/{address}#code'
    driver.get(url)

    time.sleep(2)  # Wait for page to load

    # Find the button and click it
    button = driver.find_element(By.CSS_SELECTOR, "a.js-clipboard.btn.btn-sm.btn-icon.btn-secondary.me-1")
    button.click()

    time.sleep(2)  # Wait for the clipboard to get the text

    # Get text from clipboard
    contract_source = pyperclip.paste()

    driver.quit()

    return contract_source

async def main():
    db_path = './filtered_messages.db'  # The path to the db file

    # Connect to the SQLite database
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row  # This enables column access by name: row['column_name'] 

        while True:  # Infinite loop
            # Get the cursor
            async with db.cursor() as cursor:
                # Execute the SQL command
                await cursor.execute('SELECT eth_address FROM filtered_messages')

                # Fetch all rows
                rows = await cursor.fetchall()

                for row in rows:
                    # Run the get_contract_source function in a separate thread
                    loop = asyncio.get_running_loop()
                    contract_source = await loop.run_in_executor(None, get_contract_source, row['eth_address'])
                    print(contract_source)

            # Sleep for a while before the next loop iteration
            await asyncio.sleep(5)  # Adjust the sleep duration as needed

# Run the main function
asyncio.run(main())
