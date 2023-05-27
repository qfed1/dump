from keys import token
import logging
import sqlite3
import asyncio
import re
from telegram import __version__ as TG_VER
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from collections import defaultdict

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

timer_beep_counter = int(input("Enter a starting beep counter: "))
MAX_MESSAGE_LENGTH = 4030

last_refresh_time = 0
db_path = 'filter_gold.db'  # Path to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create a dictionary to store the count of warnings for each job
job_warnings = defaultdict(int)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! Use /set <seconds> to set a timer")

async def fetch_message_after_wait(offset):
    await asyncio.sleep(5)
    cursor.execute('SELECT eth_address, message FROM filtereed_messages LIMIT 1 OFFSET ?', (offset,))
    return cursor.fetchone()

import telegram.error

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    global timer_beep_counter
    global last_refresh_time
    job = context.job

    if job_warnings[job.name] >= 5:
        # Skip this execution if we've had 5 warnings in a row
        return

    cursor.execute('SELECT eth_address, message FROM filtered_messages LIMIT 1 OFFSET ?', (timer_beep_counter,))
    row = cursor.fetchone()
    if row is None:
        row = await fetch_message_after_wait(timer_beep_counter)
        if row is None:
            last_refresh_time = 0
            cursor.execute('SELECT eth_address, message FROM filtered_messages LIMIT 1') 
            row = cursor.fetchone()

    eth_address, message_text = row if row else ("", "")
    message_text = message_text.replace("Make sure to join our Alpha Community: @NovelApes so we can make bank together during the next bulla!", "")

    # Extract Ethereum address between "Etherscan The Address" and "Comment" and remove from message_text
    match = re.search(r"Etherscan The Address(.*?)Comment", message_text)
    if match:
        extracted_address = match.group(1).strip()
        message_text = message_text.replace(match.group(0), "")

        # Add Etherscan link with extracted address
        links_text += f"\nEtherscan: https://etherscan.io/token/{extracted_address}"

    # Rest of the code...

if __name__ == "__main__":
    main()
