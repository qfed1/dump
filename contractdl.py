

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pyperclip

def get_contract_source(address):
    # You need to have a webdriver downloaded and provide its path here
    # You can download a webdriver from: https://sites.google.com/a/chromium.org/chromedriver/downloads
    driver = webdriver.Chrome('/path/to/chromedriver')

    url = f'https://etherscan.io/address/{address}#code'
    driver.get(url)

    time.sleep(2)  # Wait for page to load

    # Find the button and click it
    button = driver.find_element(By.XPATH, "//a[contains(@class,'js-clipboard')]")
    button.click()

    time.sleep(2)  # Wait for the clipboard to get the text

    # Get text from clipboard
    contract_source = pyperclip.paste()

    driver.quit()

    return contract_source

# Example usage:
address = '0x36a17fbd22fb6b77f55ab797869700b663b026b6'
print(get_contract_source(address))

