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
    await application.bot.sendMessage(chat_id=chat, text=f"<pre>{msg}</pre>", parse_mode='HTML')

# other functions remain unchanged

async def main():
    await init_db("sent_messages.db")  # initialize the sent_messages database
    while True:
        rows = await fetch_rows_from_db("filtered_gold.db")
        for row in rows:
            msg = str(row)  # convert row data to string
            if not await is_sent("sent_messages.db", msg):
                asyncio.sleep(2)
                await send_more(chat_id, msg)
                await mark_as_sent("sent_messages.db", msg)
        await asyncio.sleep(5)  # wait for 5 seconds before polling again

# Run the main function
asyncio.run(main())
