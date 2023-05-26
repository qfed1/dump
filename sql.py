import sqlite3
import os

def print_db_schema(db_path):
    if not os.path.exists(db_path):
        print(f"The specified database path does not exist: {db_path}")
        return

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # For each table, get and print the schema
    for table in tables:
        print(f"Table: {table[0]}")
        cursor.execute(f"PRAGMA table_info({table[0]});")
        
        # Fetch and print the schema
        schema = cursor.fetchall()
        for column in schema:
            print(column)

    # Close the connection
    conn.close()


db_path1 = r"C:\Users\evanb\git\AI\NEWFILES\OBEYORDIE\messages.db"
db_path2 = r"C:\Users\evanb\git\AI\NEWFILES\OBEYORDIE\new_messages.db"

print_db_schema(db_path1)
print_db_schema(db_path2)
