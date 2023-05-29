import aiosqlite
import asyncio
import re
import os

# Connect to the SQLite database
db_path = os.path.join(os.getcwd(), 'new_messages420.db')
new_db_path = os.path.join(os.getcwd(), 'filter_gold.db')

# Your filtering function
async def filter_comments(comment):
    # Find content between "Potential TG:" and "Etherscan Chart"
    result = re.search('Potential TG:(.*?)Etherscan Chart', comment[1])
    # Find content between "Contract uniqueness:" and "Potential TG:"
    unique_result = re.search('Contract uniqueness:(.*?)Potential TG:', comment[1])

    # If we found a match and it doesn't contain "Found Honeypot? UNKNOWN" or "Honeypot? YES!! - but this can change"
    # and the content between "Contract uniqueness:" and "Potential TG:" is "Unique contract"
    if result and unique_result and "Found Honeypot? UNKNOWN" not in result.group(1) and "Honeypot? YES!! - but this can change" not in result.group(1) and "Unique contract" in unique_result.group(1):
        return comment  # Return the comment if it matches the criteria
    else:
        return None

# Main polling function
async def poll_db(db_path, new_db_path):
    last_id = 0
    while True:
        async with aiosqlite.connect(db_path) as db:
            cur = await db.cursor()
            await cur.execute(f'SELECT * FROM eth_messages WHERE rowid > {last_id}')
            comments = await cur.fetchall()
            last_id = max([comment[0] for comment in comments], default=last_id)

            async with aiosqlite.connect(new_db_path) as new_db:
                new_cur = await new_db.cursor()
                for comment in comments:
                    filtered_comment = await filter_comments(comment)
                    if filtered_comment is not None:
                        await new_cur.execute('INSERT INTO filtered_messages VALUES (?, ?)', filtered_comment)
                await new_db.commit()

        await asyncio.sleep(5)

# Asyncio main function
async def main():
    # Create new database and table if not exists
    async with aiosqlite.connect(new_db_path) as db:
        cur = await db.cursor()
        await cur.execute('CREATE TABLE IF NOT EXISTS filtered_messages (eth_address TEXT, message TEXT)')
        await db.commit()

    # Start polling the original database
    await poll_db(db_path, new_db_path)

# Run the asyncio main function
asyncio.run(main())
