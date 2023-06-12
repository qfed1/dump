from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyperclip

def get_contract_source(address):
    # Setup webdriver
    webdriver_service = Service(ChromeDriverManager().install())
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

# Example usage:
address = '0x36a17fbd22fb6b77f55ab797869700b663b026b6'
print(get_contract_source(address))