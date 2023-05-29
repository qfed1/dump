import asyncio
import telegram
from telegram.ext import ApplicationBuilder
from keys import token as token1

bot_token = token1
chat_id = "6078159404"

# using telegram.Bot
async def send(chat, msg):
    await telegram.Bot(bot_token).sendMessage(chat_id=chat, text=msg)

asyncio.run(send(chat_id, 'Hello there!'))

# using ApplicationBuilder
async def send_more(chat, msg):
    application = ApplicationBuilder().token(bot_token).build()
    await application.bot.sendMessage(chat_id=chat, text=msg)

asyncio.run(send_more(chat_id, 'Hello there!'))
