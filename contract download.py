import requests
from bs4 import BeautifulSoup

def get_contract_source(address):
    url = f'https://etherscan.io/address/{address}#code'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        contract_source = soup.find('pre', {'class': 'js-sourcecopyarea', 'id': 'editor'})
        return contract_source.text
    else:
        return None

# Example usage:
address = '<contract-address>'
print(get_contract_source(address))
