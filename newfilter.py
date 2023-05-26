import sqlite3
import re
import os

# Connect to the SQLite database
db_path = os.path.join(os.getcwd(), 'new_messages420.db')
conn = sqlite3.connect(db_path)

# Create a cursor object
cur = conn.cursor()

# Execute a query to fetch all rows from the table
cur.execute('SELECT * FROM eth_messages')

# Fetch all rows as a list of tuples
comments = cur.fetchall()

# Your filtering function
def filter_comments(comments):
    filtered_comments = []
    for comment in comments:
        # Find content between "Potential TG:" and "Etherscan Chart"
        result = re.search('Potential TG:(.*?)Etherscan Chart', comment[1])
        # Find content between "Contract uniqueness:" and "Potential TG:"
        unique_result = re.search('Contract uniqueness:(.*?)Potential TG:', comment[1])

        # If we found a match and it doesn't contain "Found Honeypot? UNKNOWN" or "Honeypot? YES!! - but this can change"
        # and the content between "Contract uniqueness:" and "Potential TG:" is "Unique contract"
        if result and unique_result and "Found Honeypot? UNKNOWN" not in result.group(1) and "Honeypot? YES!! - but this can change" not in result.group(1) and "Unique contract" in unique_result.group(1):
            # Add to filtered comments
            filtered_comments.append(comment)  # Add the whole comment

    return filtered_comments

filtered_comments = filter_comments(comments)

# Close the connection
conn.close()

# Save to new database
new_db_path = os.path.join(os.getcwd(), 'filter_gold.db')
conn_new = sqlite3.connect(new_db_path)
cur_new = conn_new.cursor()

# Create a new table in the new database
cur_new.execute('CREATE TABLE filtered_messages (eth_address TEXT, message TEXT)')

# Insert the filtered comments into the new table
cur_new.executemany('INSERT INTO filtered_messages VALUES (?, ?)', filtered_comments)

# Commit the changes and close the connection
conn_new.commit()
conn_new.close()
