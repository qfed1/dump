from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyperclip
import asyncio
import aiosqlite

def get_contract_source(address):
    webdriver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=webdriver_service)

    url = f'https://etherscan.io/address/{address}#code'
    driver.get(url)

    time.sleep(2)  # Wait for page to load

    button = driver.find_element(By.CSS_SELECTOR, "a.js-clipboard.btn.btn-sm.btn-icon.btn-secondary.me-1")
    button.click()

    time.sleep(2)  # Wait for the clipboard to get the text

    contract_source = pyperclip.paste()

    driver.quit()

    return contract_source

async def read_db_and_scrape():
    db_path = './filtered_gold.db'  # The path to the db file

    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row

        while True:
            async with db.cursor() as cursor:
                await cursor.execute('SELECT eth_address FROM filtered_messages')
                rows = await cursor.fetchall()

                for row in rows:
                    contract_source = get_contract_source(row['eth_address'])
                    print(contract_source)

            await asyncio.sleep(5)

asyncio.run(read_db_and_scrape())
