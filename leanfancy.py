from keys import token
import logging
import sqlite3
import asyncio
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

    # Create the links with the fetched eth_address
    links_text = "\n\n".join([
        f"Honeypot: https://honeypot.is/ethereum.html?address={eth_address}",
        f"Tokensniffer: https://tokensniffer.com/token/{eth_address}",
        f"Dextools: https://www.dextools.io/app/ether/pair-explorer/{eth_address}",
        f"Dexscreener: https://dexscreener.com/ethereum/{eth_address}",
        f"coinscan: https://www.coinscan.com/tokens/{eth_address}",
        f"Holders: https://etherscan.io/token/{eth_address}#balances",
        f"Owner: https://etherscan.io/address/{eth_address}",
        f"Contract: https://etherscan.io/token/{eth_address}",
        f"Uniswap: https://app.uniswap.org/#/swap?outputCurrency={eth_address}",
        f"1inch: https://app.1inch.io/#/1/unified/swap/ETH/{eth_address}",
    ])

    # Split the message text into lines at each "|" character
    message_text = "\n\n".join(message_text.split("|"))

    # Replace the desired phrases
    if message_text.startswith("Token Update Name:"):
        message_text = "🪙 HYPE TOKEN UPDATE🚀" + message_text[19:]
    elif message_text == "New Token Found !!":
        message_text = "🪙 HYPE TOKEN APPROVED 🚀"

    message = f"Row {timer_beep_counter}: {eth_address} - {message_text}" if eth_address.strip() and message_text.strip() else "No more messages"

    # Add the links to the end of the message
    message += "\n\n" + links_text

    try:
        if len(message) <= MAX_MESSAGE_LENGTH:
            await context.bot.send_message(job.chat_id, text=message)
        else:
            messages = [message[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(message), MAX_MESSAGE_LENGTH)]
            for i, msg in enumerate(messages, 1):
                await context.bot.send_message(job.chat_id, text=f"{msg}\n\nPart {i}/{len(messages)}")
    except telegram.error.RetryAfter as e:
        await asyncio.sleep(e.retry_after)  # Wait for the specified time before retrying
        job_warnings[job.name] += 1  # Increment the warning count for this job
    else:
        job_warnings[job.name] = 0  # Reset the count if we successfully sent a message

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
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))

    application.run_polling()

if __name__ == "__main__":
    main()
