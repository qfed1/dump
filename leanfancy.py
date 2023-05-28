import asyncio
import logging
import os
import re
import subprocess
import sqlite3
from collections import defaultdict
from telegram import __version__ as TG_VER
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from keys import token

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

db_path = 'filter_gold.db'  # Path to the SQLite database
archive_db_path = 'filter_gold_archive.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

job_warnings = defaultdict(int)
timer_beep_counter = int(input("Enter a starting beep counter: "))
MAX_MESSAGE_LENGTH = 4030
last_refresh_time = 0

def archive_db():
    if os.path.exists(archive_db_path):
        os.remove(archive_db_path)
    
    shutil.copyfile(db_path, archive_db_path)

def check_in_archive(eth_address, message):
    conn_archive = sqlite3.connect(archive_db_path)
    cursor_archive = conn_archive.cursor()

    cursor_archive.execute('SELECT * FROM filtered_messages WHERE eth_address = ? AND message = ?', (eth_address, message))
    data = cursor_archive.fetchone()

    return data is not None

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
        return

    cursor.execute('SELECT eth_address, message FROM filtered_messages LIMIT 1 OFFSET ?', (timer_beep_counter,))
    row = cursor.fetchone()
    if row is None:
        row = await fetch_message_after_wait(timer_beep_counter)
        if row is None:
            print("Reached end of file, restarting the entire process...")
            main()  # Restart the main function (this will restart the whole process)

    eth_address, message_text = row if row else ("", "")
    if check_in_archive(eth_address, message_text):
        return

    message_text = message_text.replace("Make sure to join our Alpha Community: @NovelApes so we can make bank together during the next bulla!", "")

    start = message_text.find("Etherscan The Address") + len("Etherscan The Address")
    end = message_text.find("Comment")
    etherscan_address = message_text[start:end].strip()

    message_text = message_text[:start] + message_text[end:]

    eth_address_clean = re.search(r'0x[a-fA-F0-9]{40}', eth_address)
    eth_address_link = f"https://etherscan.io/address/{eth_address_clean.group()}" if eth_address_clean else ""

    etherscan_address_link = f"https://etherscan.io/address/{etherscan_address}"

    links_text = "\n\n".join([
        f"Honeypot: https://honeypot.is/ethereum.html?address={eth_address}",
        f"Tokensniffer: https://tokensniffer.com/token/{eth_address}",
        f"Dextools: https://www.dextools.io/app/ether/pair-explorer/{eth_address}",
        f"Dexscreener: https://dexscreener.com/ethereum/{eth_address}",
        f"coinscan: https://www.coinscan.com/tokens/{eth_address}",
        f"Holders: https://etherscan.io/token/{eth_address}/#balances",
        f"Owner: https://etherscan.io/address/{eth_address}",
        f"Contract: https://etherscan.io/token/{eth_address}",
        f"Uniswap: https://app.uniswap.org/#/swap?outputCurrency={eth_address}",
        f"1inch: https://app.1inch.io/#/1/unified/swap/ETH/{eth_address}",
        f"Etherscan: {etherscan_address_link}"
    ])

    scanner_index = message_text.find("Scanners: Honeypot")
    if scanner_index != -1:
        message_text = message_text[:scanner_index] + "Scanners: "

    message_text = "\n\n".join(message_text.split("|"))

    message = f"Row {timer_beep_counter}: {eth_address_link}\n\n{message_text}\n\n{links_text}"

    try:
        if len(message) <= MAX_MESSAGE_LENGTH:
            await context.bot.send_message(job.chat_id, text=message)
        else:
            messages = [message[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(message), MAX_MESSAGE_LENGTH)]
            for i, msg in enumerate(messages, 1):
                await context.bot.send_message(job.chat_id, text=f"{msg}\n\nPart {i}/{len(messages)}")
    except telegram.error.RetryAfter as e:
        await asyncio.sleep(e.retry_after)  
        job_warnings[job.name] += 1  
    else:
        job_warnings[job.name] = 0  

    timer_beep_counter += 1
    print(f"Beep! {job.data} seconds are over! This is beep number {timer_beep_counter}.")

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    try:
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds> DO NOT SET LOWER THAN 0.43 SECONDS UNDER NO CIRCUMSTANCES!!!")

async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)

def main() -> None:
    # Archive data before deleting the db
    archive_db()

    if os.path.exists(db_path):
        os.remove(db_path)

    subprocess.run(["python3", "filter.py"])
    subprocess.run(["python3", "newfilter.py"])

    global conn, cursor
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    app = Application(token, use_context=True)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set", set_timer, pass_args=True, run_async=True))
    app.add_handler(CommandHandler("unset", unset, run_async=True))

    app.run()

if __name__ == "__main__":
    main()
