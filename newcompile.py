import sqlite3
import re
import os

# The Ethereum address pattern
eth_addr_pattern = re.compile(r'\b0x[a-fA-F0-9]{40}\b')

# List of database paths
db_files = [
    "C:/Users/evanb/git/AI/NEWFILES/OBEYORDIE/messages.db",
    "C:/Users/evanb/git/AI/NEWFILES/OBEYORDIE/messagesvolume1.db"
]

# Create a list of dictionaries to store Ethereum addresses and associated messages from each database
eth_addr_messages = [{} for _ in db_files]

for idx, db_file in enumerate(db_files):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # Query to select all messages
    c.execute("SELECT message_text FROM messages")
    rows = c.fetchall()

    for row in rows:
        message = row[0]

        # Find Ethereum addresses in the message
        eth_addresses = eth_addr_pattern.findall(message)

        for eth_addr in eth_addresses:
            eth_addr_messages[idx][eth_addr] = message

    conn.close()

# Find common Ethereum addresses in the two databases and concatenate associated messages
common_eth_addr_messages = {}
for eth_addr in eth_addr_messages[0]:
    if eth_addr in eth_addr_messages[1]:
        common_eth_addr_messages[eth_addr] = eth_addr_messages[0][eth_addr] + " " + eth_addr_messages[1][eth_addr]

# Create a new database in the same directory as the script
new_db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "new_messages.db")
new_conn = sqlite3.connect(new_db_path)
new_c = new_conn.cursor()

# Create a new table in the new database
new_c.execute("""
CREATE TABLE IF NOT EXISTS eth_messages (
    eth_address TEXT,
    message TEXT
)
""")

# Populate the new table with the common Ethereum addresses and their corresponding concatenated messages
for eth_addr, message in common_eth_addr_messages.items():
    new_c.execute("INSERT INTO eth_messages (eth_address, message) VALUES (?, ?)",
                  (eth_addr, message))

new_conn.commit()
new_conn.close()

print(f"New database created at {new_db_path}")
