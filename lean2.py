import logging
import sqlite3
import asyncio
from telegram import Bot, Update
from telegram.ext import CommandHandler, CallbackContext, Updater
import pkg_resources
from collections import defaultdict

TG_VER = pkg_resources.get_distribution("python-telegram-bot").version

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

timer_beep_counter = int(input("Enter a starting beep counter: "))
MAX_MESSAGE_LENGTH = 4030

last_refresh_time = 0
db_path = 'filter_gold.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

job_warnings = defaultdict(int)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hi! Use /set <seconds> to set a timer")

async def fetch_message_after_wait(offset):
    await asyncio.sleep(5)
    cursor.execute('SELECT eth_address, message FROM filtereed_messages LIMIT 1 OFFSET ?', (offset,))
    return cursor.fetchone()

async def alarm(context: CallbackContext) -> None:
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
            last_refresh_time = 0
            cursor.execute('SELECT eth_address, message FROM filtered_messages LIMIT 1') 
            row = cursor.fetchone()

    eth_address, message_text = row if row else ("", "")

    if message_text.startswith("Token Update Name:"):
        message_text = "🪙 HYPE TOKEN UPDATE🚀" + message_text[19:]
    elif message_text == "New Token Found !!":
        message_text = "🪙 HYPE TOKEN APPROVED 🚀"

    message = f"Row {timer_beep_counter}: {eth_address} - {message_text}" if eth_address.strip() and message_text.strip() else "No more messages"

    try:
        if len(message) <= MAX_MESSAGE_LENGTH:
            await context.bot.send_message(job.context, text=message)
        else:
            messages = [message[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(message), MAX_MESSAGE_LENGTH)]
            for i, msg in enumerate(messages, 1):
                await context.bot.send_message(job.context, text=f"{msg}\n\nPart {i}/{len(messages)}")
    except telegram.error.RetryAfter as e:
        await asyncio.sleep(e.retry_after)
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

async def set_timer(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_message.chat_id
    try:
        due = int(context.args[0])
        if due < 0:
            await update.message.reply_text("Sorry we can't go back to the future!")
            return
        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(alarm, due, context=chat_id, name=str(chat_id))
        text = "Timer successfully set!" if not job_removed else "Timer is already set - I'm replacing the old one with the new one you just set."
        await update.message.reply_text(text)
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /set <seconds>")

def main() -> None:
    # token input
    token = input("Enter your token: ")
    updater = Updater(token)

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("set", set_timer))
    updater.start_polling()

    updater.idle()

if __name__ == "__main__":
    main()
