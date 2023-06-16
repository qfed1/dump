import os
import subprocess
import sqlite3

# Path to the directory containing the slither executable
# Replace with your actual path
slither_dir = "/root/Desktop/dump/slither"

# Change to the slither directory
os.chdir(slither_dir)

# Connect to the SQLite database
conn = sqlite3.connect('filtered_gold.db')

# Create a cursor
cur = conn.cursor()

# Execute a SQL command to get all the eth_address
cur.execute("SELECT eth_address FROM filtered_messages")

# Fetch all the results
eth_addresses = cur.fetchall()

for address_tuple in eth_addresses:
    address = address_tuple[0]  # Get the address from the tuple

    command = ["slither", address, "--print", "human-summary"]

    # Launch the subprocess with the given command.
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the command: {e}")
        continue  # Skip to the next address if an error occurred

    # If the command completed successfully, print the command's output.
    print(result.stdout)

# Close the connection
conn.close()
