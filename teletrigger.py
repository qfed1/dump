import asyncio
import aiosqlite
from telegram.ext import ApplicationBuilder
from keys import token as token1
from keys import chatidmaster as ch1t

bot_token = token
chat_id = ch1t

# using ApplicationBuilder
async def send_more(chat, msg):
    application = ApplicationBuilder().token(bot_token).build()
    await application.bot.sendMessage(chat_id=chat, text=msg)

# Function to retrieve rows from database
async def fetch_rows_from_db(db_path):
    db = await aiosqlite.connect(db_path)
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM gold")
    rows = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return rows

# Main function to fetch data from database and send it
async def main():
    rows = await fetch_rows_from_db("filtered_gold.db")
    for row in rows:
        msg = str(row)  # convert row data to string
        await send_more(chat_id, msg)

# Run the main function
asyncio.run(main())
