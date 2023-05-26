import sqlite3

def clear_database(db_path):
    # Connect to the database
    conn = sqlite3.connect(db_path)

    # Create a cursor object
    cur = conn.cursor()

    # Get the list of all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()

    # For each table, delete all rows
    for table in tables:
        cur.execute(f"DELETE FROM {table[0]};")

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

db_path = r"C:\Users\evanb\git\AI\NEWFILES\OBEYORDIE\telegram_messages.db"
clear_database(db_path)
