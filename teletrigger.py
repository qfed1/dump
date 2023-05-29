import asyncio
import aiosqlite
from telegram.ext import ApplicationBuilder
from keys import token
from keys import chatidmaster

bot_token = token
chat_id = chatidmaster

# using ApplicationBuilder
async def send_more(chat, msg):
    application = ApplicationBuilder().token(bot_token).build()
    await application.bot.sendMessage(chat_id=chat, text=msg)

# Function to retrieve rows from database
async def fetch_rows_from_db(db_path, offset=0):
    db = await aiosqlite.connect(db_path)
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM gold LIMIT -1 OFFSET ?", (offset,))
    rows = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return rows

# Main function to fetch data from database and send it
async def main():
    offset = 0
    while True:
        rows = await fetch_rows_from_db("filtered_gold.db", offset)
        if rows:
            offset += len(rows)
            for row in rows:
                msg = str(row)  # convert row data to string
                await send_more(chat_id, msg)
        await asyncio.sleep(5)  # wait for 5 seconds before polling again

# Run the main function
asyncio.run(main())
