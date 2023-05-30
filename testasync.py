import sqlite3

# connect to the SQLite database
connection = sqlite3.connect('filter_gold.db')

# create a cursor object using cursor() method
cursor = connection.cursor()

# define an Ethereum address and a message for the test entry
eth_address = '0x123abc...'
message = 'Thisewkjs a test message.'

# prepare SQL query
sql = '''INSERT INTO filtered_messages(eth_address, message) VALUES(?,?)'''

# execute the SQL statement
cursor.execute(sql, (eth_address, message))

# commit the changes and close the connection
connection.commit()

# close the connection
connection.close()
