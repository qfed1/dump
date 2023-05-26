import sqlite3
import pandas as pd

# Connect to the source database
source_connection = sqlite3.connect(r'C:\Users\evanb\git\AI\NEWFILES\OBEYORDIE\new_messages420.db')

# Load the data into a pandas DataFrame
df = pd.read_sql_query("SELECT * FROM eth_messages", source_connection)

# Perform the filtering
df = df[df['message'].str.contains("Found Honeypot? No - but this can change|Contract uniqueness: Unique contract", case=False)]
df = df[~df['message'].str.contains("similar contracts found|Found Honeypot? UNKNOWN", case=False)]

# Connect to the target database
target_connection = sqlite3.connect(r'C:\Users\evanb\git\AI\NEWFILES\OBEYORDIE\new_messages1.db')

# Write the data from the DataFrame to the new SQLite database
df.to_sql('eth_messages', target_connection, if_exists='replace', index=False)

# Close the connections
source_connection.close()
target_connection.close()
