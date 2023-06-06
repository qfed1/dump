from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import pyperclip
import subprocess
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

webdriver_service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)


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

    # Save the contract source to a .sol file
    filename = f'{address}.sol'
    with open(filename, 'w') as f:
        f.write(contract_source)

    # Run Slither analysis on the file
    sol_filename = f'{filename}.sol'
    slither_path = "/root/Desktop/dump/slither"
    result = subprocess.run([slither_path, sol_filename], stdout=subprocess.PIPE)
    print(result.stdout.decode('utf-8'))

# Example usage:
address = '0x36a17fbd22fb6b77f55ab797869700b663b026b6'
get_contract_source(address)
