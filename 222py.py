import time
import pyperclip
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

def get_contract_source(address):
    TAKE_IT_EASY = True

    if TAKE_IT_EASY:
        sleep = time.sleep
    else:
        sleep = lambda n: print(
            "we could be sleeping %d seconds here, but we don't" % n
        )

    options = uc.ChromeOptions()

    # You might want to comment these lines if you don't run on a headless Linux server
    #options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    with uc.Chrome(options=options) as driver:
        url = f'https://etherscan.io/address/{address}#code'
        driver.get(url)
    
        # Pause script and wait for user to press Enter
        input("Press Enter to continue...")
    
        # Find the button and click it
        button = driver.find_element(By.CSS_SELECTOR, "a.js-clipboard.btn.btn-sm.btn-icon.btn-secondary.me-1")
        button.click()
    
        sleep(2)  # Wait for the clipboard to get the text
    
        # Get text from clipboard
        contract_source = pyperclip.paste()

    return contract_source

# Example usage:
address = '0x433C8046CfCD5701f1813Dd4988045d205Dd9F62'
print(get_contract_source(address))


with open(f'{address}.sol', 'w') as file:
    file.write(contract_source)
