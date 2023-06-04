

import requests
from bs4 import BeautifulSoup

def get_contract_source(address):
    url = f'https://etherscan.io/address/{address}#code'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        contract_source_lines = soup.select('div.ace_content > div.ace_layer.ace_marker-layer > div.ace_line_group')

        # Join the text of each line into one string
        contract_source = '\n'.join(line.text for line in contract_source_lines)

        return contract_source
    else:
        return None

# Example usage:
address = '0x36a17fbd22fb6b77f55ab797869700b663b026b6'
print(get_contract_source(address))
