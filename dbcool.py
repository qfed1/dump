import sqlite3
import re
import time

db_path = 'filter_gold.db'  # Path to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

new_db_path = 'filtered_gold.db'  # Path to the new SQLite database
new_conn = sqlite3.connect(new_db_path)
new_cursor = new_conn.cursor()

# Create a new table in the new database
new_cursor.execute('CREATE TABLE IF NOT EXISTS filtered_messages(eth_address TEXT, message TEXT)')

cursor.execute('SELECT COUNT(*) FROM filtered_messages')
row_count = cursor.fetchone()[0]
print(f"Total rows to process: {row_count}")

for offset in range(row_count):
    cursor.execute('SELECT eth_address, message FROM filtered_messages LIMIT 1 OFFSET ?', (offset,))
    row = cursor.fetchone()

    eth_address, message_text = row if row else ("", "")
    message_text = message_text.replace("Make sure to join our Alpha Community: @NovelApes so we can make bank together during the next bulla!", "")
    start = message_text.find("Etherscan The Address") + len("Etherscan The Address")
    end = message_text.find("Comment")
    etherscan_address = message_text[start:end].strip()
    message_text = message_text[:start] + message_text[end:]
    eth_address_clean = re.search(r'0x[a-fA-F0-9]{40}', eth_address)
    eth_address_link = f"https://etherscan.io/address/{eth_address_clean.group()}" if eth_address_clean else ""
    etherscan_address_link = f"https://etherscan.io/address/{etherscan_address}"
    scanner_index = message_text.find("Scanners: Honeypot")
    if scanner_index != -1:
        message_text = message_text[:scanner_index] + "Scanners: "
    message_text = "\n\n".join(message_text.split("|"))
    links_text = "\n\n".join([
        "Honeypot: " + f"https://honeypot.is/ethereum.html?address={eth_address}",
        "Tokensniffer: " + f"https://tokensniffer.com/token/{eth_address}",
        "Dextools: " + f"https://www.dextools.io/app/ether/pair-explorer/{eth_address}",
        "Dexscreener: " + f"https://dexscreener.com/ethereum/{eth_address}",
        "coinscan: " + f"https://www.coinscan.com/tokens/{eth_address}",
        "Holders: " + f"https://etherscan.io/token/{eth_address}/#balances",
        "Owner: " + f"https://etherscan.io/address/{eth_address}",
        "Contract: " + f"https://etherscan.io/token/{eth_address}",
        "Uniswap: " + f"https://app.uniswap.org/#/swap?outputCurrency={eth_address}",
        "1inch: " + f"https://app.1inch.io/#/1/unified/swap/ETH/{eth_address}",
        "Etherscan: " + etherscan_address_link
    ])
    new_message = f"Row {offset}: {eth_address_link}\n\n{message_text}\n\nResources:\n\n{links_text}"
    new_cursor.execute('INSERT INTO filtered_messages VALUES (?, ?)', (eth_address, new_message))
    if offset % 1000 == 0:  # commit every 1000 inserts to speed up the process
        new_conn.commit()
        print(f"Processed {offset} rows...")

new_conn.commit()  # commit any remaining inserts

print("Processing complete!")
