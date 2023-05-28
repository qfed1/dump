from keys import token
import logging
import sqlite3
import asyncio
import os
import re
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from collections import defaultdict
import subprocess
from time import sleep

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

timer_beep_counter = int(input("Enter a starting beep counter: "))
MAX_MESSAGE_LENGTH = 4030

db_path = 'filter_gold.db'
db_archive_path = 'filter_gold_archive.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
conn_archive = sqlite3.connect(db_archive_path)
cursor_archive = conn_archive.cursor()

# Create a dictionary to store the count of warnings for each job
job_warnings = defaultdict(int)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hi! Use /set <seconds> to set a timer")

def alarm(context: CallbackContext) -> None:
    global timer_beep_counter
    job = context.job

    if job_warnings[job.name] >= 5:
        return

    cursor.execute('SELECT eth_address, message FROM filtered_messages LIMIT 1 OFFSET ?', (timer_beep_counter,))
    row = cursor.fetchone()

    if row is None:
        sleep(5)
        cursor.execute('SELECT eth_address, message FROM filtered_messages LIMIT 1 OFFSET ?', (timer_beep_counter,))
        row = cursor.fetchone()

    eth_address, message_text = row if row else ("", "")
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
            cursor_archive.execute("INSERT INTO filtered_messages (eth_address, message) VALUES (?, ?)", (eth_address, message))
            conn_archive.commit()
            context.bot.send_message(job.context, text=message)
        else:
            messages = [message[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(message), MAX_MESSAGE_LENGTH)]
            for i, msg in enumerate(messages, 1):
                context.bot.send_message(job.context, text=f"{msg}\n\nPart {i}/{len(messages)}")
    except telegram.error.RetryAfter as e:
        sleep(e.retry_after)
        job_warnings[job.name] += 1
    else:
        job_warnings[job.name] = 0

    timer_beep_counter += 1
    print(f"Beep! {job.interval} seconds are over! This is beep number {timer_beep_counter}.")

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

def set_timer(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        due = float(context.args[0])
        if due < 0:
            update.message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(alarm, due, context=chat_id, name=str(chat_id))

        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text("Usage: /set <seconds> DO NOT SET LOWER THAN 0.43 SECONDS UNDER NO CIRCUMSTANCES!!!")

def unset(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    update.message.reply_text(text)

def main():
    if os.path.exists(db_path):
        os.remove(db_path)

    os.system("python3 filter.py")
    os.system("python3 newfilter.py")

    cursor_archive.execute("CREATE TABLE IF NOT EXISTS filtered_messages (eth_address TEXT, message TEXT)")

    updater = Updater(token=token)
    updater.add_handler(CommandHandler("start", start))
    updater.add_handler(CommandHandler("set", set_timer))
    updater.add_handler(CommandHandler("unset", unset))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
