import asyncio
import aiosqlite
from telegram.ext import ApplicationBuilder
from keys import token as token1
from keys import chatidmaster

bot_token = token1
chat_id = chatidmaster

# using ApplicationBuilder
async def send_more(chat, msg):
    application = ApplicationBuilder().token(bot_token).build()
    await application.bot.sendMessage(chat_id=chat, text=msg)

# Function to retrieve rows from database
async def fetch_rows_from_db(db_path):
    db = await aiosqlite.connect(db_path)
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM filtered_messages")
    rows = await cursor.fetchall()
    await cursor.close()
    await db.close()
    return rows

# Function to check if a message is in the sent_messages database
async def is_sent(db_path, msg):
    db = await aiosqlite.connect(db_path)
    cursor = await db.cursor()
    await cursor.execute("SELECT * FROM messages WHERE message = ?", (msg,))
    row = await cursor.fetchone()
    await cursor.close()
    await db.close()
    return row is not None

# Function to add a message to the sent_messages database
async def mark_as_sent(db_path, msg):
    db = await aiosqlite.connect(db_path)
    cursor = await db.cursor()
    await cursor.execute("INSERT INTO messages (message) VALUES (?)", (msg,))
    await db.commit()
    await cursor.close()
    await db.close()

# Function to initialize the sent_messages database
async def init_db(db_path):
    db = await aiosqlite.connect(db_path)
    cursor = await db.cursor()
    await cursor.execute("CREATE TABLE IF NOT EXISTS messages (message TEXT)")
    await cursor.execute("PRAGMA journal_mode=WAL")
    await db.commit()
    await cursor.close()
    await db.close()

# Main function to fetch data from database and send it
async def main():
    await init_db("sent_messages.db")  # initialize the sent_messages database
    while True:
        rows = await fetch_rows_from_db("filtered_gold.db")
        for row in rows:
            msg = row[1]  # Get the message from the row
            # Remove unwanted characters
            msg = msg.replace('\\n\\n', '\n\n').replace('\\n', '')
            if not await is_sent("sent_messages.db", msg):
                await asyncio.sleep(2)
                await send_more(chat_id, msg)
                await mark_as_sent("sent_messages.db", msg)
        await asyncio.sleep(5)  # wait for 5 seconds before polling again

# Run the main function
asyncio.run(main())
