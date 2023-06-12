import aiosqlite
import asyncio

async def main():
    db_path = './filtered_messages.db'  # The path to the db file

    # Connect to the SQLite database
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row  # This enables column access by name: row['column_name'] 

        while True:  # Infinite loop
            # Get the cursor
            async with db.cursor() as cursor:
                # Execute the SQL command
                await cursor.execute('SELECT eth_address FROM filtered_messages')

                # Fetch all rows
                rows = await cursor.fetchall()

                for row in rows:
                    print(row['eth_address'])

            # Sleep for a while before the next loop iteration
            await asyncio.sleep(5)  # Adjust the sleep duration as needed

# Run the main function
asyncio.run(main())
