
from keys import token
import logging
import sqlite3
import asyncio
from telegram import __version__ as TG_VER
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

timer_beep_counter = int(input("Enter a starting beep counter: "))

last_refresh_time = 0
db_path = 'messages.db'  # Path to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! Use /set <seconds> to set a timer")

async def fetch_message_after_wait(offset):
    await asyncio.sleep(5)
    cursor.execute('SELECT message_text FROM messages LIMIT 1 OFFSET ?', (offset,))
    return cursor.fetchone()

import telegram.error

# ... (rest of your code)

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    global timer_beep_counter
    global last_refresh_time
    job = context.job

    cursor.execute('SELECT message_text FROM messages LIMIT 1 OFFSET ?', (timer_beep_counter,))
    row = cursor.fetchone()
    if row is None:
        row = await fetch_message_after_wait(timer_beep_counter)
        if row is None:
            last_refresh_time = 0
            cursor.execute('SELECT message_text FROM messages LIMIT 1') 
            row = cursor.fetchone()

    message = f"Row {timer_beep_counter}: {row[0]}" if row and row[0].strip() else "No more messages"

    try:
        await context.bot.send_message(job.chat_id, text=message)
    except telegram.error.RetryAfter as e:
        await asyncio.sleep(e.retry_after)  # Wait for the specified time before retrying

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