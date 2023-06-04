
import requests
from bs4 import BeautifulSoup

def get_contract_source(address):
    url = f'https://etherscan.io/address/{address}#code'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        contract_source = soup.select_one('pre.js-sourcecopyarea.editor.ace_editor > div.ace_scroller > div.ace_content')
        return contract_source.text if contract_source else None
    else:
        return None

# Example usage:
address = '0x36a17fbd22fb6b77f55ab797869700b663b026b6'
print(get_contract_source(address))
