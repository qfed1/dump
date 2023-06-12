from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pyperclip

def get_contract_source(address):
    # Setup webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    driver = webdriver.Chrome(executable_path='/usr/bin/chromedriver', options=options)

    url = f'https://etherscan.io/address/{address}#code'
    driver.get(url)

    # Wait for one URL change
    old_url = driver.current_url
    while old_url == driver.current_url:
        time.sleep(0.5)  # Prevent CPU hogging

    # Find the button and click it
    button = driver.find_element(By.CSS_SELECTOR, "a.js-clipboard.btn.btn-sm.btn-icon.btn-secondary.me-1")
    button.click()

    # Wait for the clipboard to get the text
    time.sleep(2)

    # Get text from clipboard
    contract_source = pyperclip.paste()

    driver.quit()

    # Save the contract source to a .sol file
    filename = f'{address}.sol'
    with open(filename, 'w') as f:
        f.write(contract_source)

    print(f'Successfully saved the contract to {filename}')

# Example usage:
address = '0x36a17fbd22fb6b77f55ab797869700b663b026b6'
get_contract_source(address)
