from fuzzywuzzy import fuzz, process
import pandas as pd
import sqlite3
import re

def extract_addresses(text):
    """Extract potential Ethereum addresses from a string of text."""
    return re.findall(r'\b0x[a-fA-F0-9]{40}\b', text)

def find_similar_rows(df1, df2, conn3, threshold=80):
    """Find similar rows between two dataframes based on fuzzy string matching and wallet addresses."""

    # Normalize the data by turning each row into a single string.
    df1_str = df1['message_text']
    df2_str = df2['message_text']

    # Create a cursor for writing to the database
    c = conn3.cursor()

    # Loop through each row in the first dataframe
    for index1, row1 in df1_str.items():
        if row1.strip() == '':
            continue  # Skip empty strings

        # Find the most similar row in the second dataframe
        best_match, score, _ = process.extractOne(row1, df2_str)

        # Check if any wallet addresses also match
        addresses1 = set(extract_addresses(row1))
        index2 = df2_str[df2_str == best_match].index[0]
        addresses2 = set(extract_addresses(df2_str.loc[index2]))

        address_match = bool(addresses1 & addresses2)  # Check if there is any common address

        # If the score meets the threshold and the addresses match, record the match
        if score > threshold and address_match:
            c.execute("INSERT INTO similar_rows VALUES (?, ?, ?, ?)", (index1, df1.loc[index1]['message_text'], index2, df2.loc[index2]['message_text']))
            conn3.commit()

# Connect to the SQLite databases
conn1 = sqlite3.connect(r'C:\Users\evanb\git\AI\NEWFILES\OBEYORDIE\messages.db')
conn2 = sqlite3.connect(r'C:\Users\evanb\git\AI\NEWFILES\OBEYORDIE\messagesvolume1.db')
conn3 = sqlite3.connect(r'C:\Users\evanb\git\AI\NEWFILES\OBEYORDIE\similar_rows.db')

# Create the table in the third database
c = conn3.cursor()
c.execute("CREATE TABLE IF NOT EXISTS similar_rows (index1 INTEGER, row1 TEXT, index2 INTEGER, row2 TEXT)")
conn3.commit()

# Use pandas to run SQL queries and load the data into dataframes
# Replace 'table1' and 'table2' with the actual table names in your databases
df1 = pd.read_sql_query("SELECT * FROM messages", conn1)
df2 = pd.read_sql_query("SELECT * FROM messages", conn2)

# Find similar rows
find_similar_rows(df1, df2, conn3, threshold=50)
