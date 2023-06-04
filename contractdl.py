

import requests
from bs4 import BeautifulSoup

def get_contract_source(address):
    url = f'https://etherscan.io/address/{address}#code'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # The HTML path provided
        path = [
            "html#html",
            "body#body",
            "main#content",
            "section#ContentPlaceHolder1_divSummary",
            "div#pills-tabContent",
            "div#contracts",
            "div.card.p-5.mb-3",
            "div#code",
            "div#dividcode",
            "div.mb-4",
            "pre#editor",
            "div.ace_scroller",
            "div.ace_content"
        ]

        # For each tag in the path, select it, and if there are multiple matches, take the first one
        element = soup
        for tag in path:
            element = element.select_one(tag)
            if element is None:
                break

        # Assuming that the last element is the one containing the contract source
        if element is not None:
            contract_source = element.text
            return contract_source
    else:
        return None

# Example usage:
address = '0x36a17fbd22fb6b77f55ab797869700b663b026b6'
print(get_contract_source(address))

