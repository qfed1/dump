import asyncio
import aiosqlite
from telegram.ext import ApplicationBuilder

bot_token = "<bot-token>"
chat_id = "<chat-id>"

# using ApplicationBuilder
async def send_more(chat, msg):
    application = ApplicationBuilder().token(bot_token).build()
    await application.bot.sendMessage(chat_id=chat, text=msg)

# Function to retrieve rows from database
async def fetch_rows_from_db(db_path, last_row_id=0):
    db = await aiosqlite.connect(db_path)
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM gold WHERE rowid > ?", (last_row_id,))
    rows = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return rows

# Main function to fetch data from database and send it
async def main():
    last_row_id = 0
    while True:
        rows = await fetch_rows_from_db("filtered_gold.db", last_row_id)
        if rows:
            last_row_id = rows[-1][0]  # assuming first column is the id
            for row in rows:
                msg = str(row)  # convert row data to string
                await send_more(chat_id, msg)
        await asyncio.sleep(5)  # wait for 5 seconds before polling again

# Run the main function
asyncio.run(main())
