from keys import token
import logging
import sqlite3
import time
from pathlib import Path
from telegram import __version__ as TG_VER
import asyncio

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

timer_beep_counter = 0
last_refresh_time = 0
db_path = "C:\\Users\\evanb\\git\\AI\\NEWFILES\\OBEYORDIE\\telegram_messages.db"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! Use /set <seconds> to set a timer")

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    global timer_beep_counter
    global last_refresh_time

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT message FROM messages ORDER BY id ASC LIMIT 1 OFFSET ?', (timer_beep_counter,))

    message = cur.fetchone()
    if message is None:
        # We've reached the end of the DB file. Refresh it.
        last_refresh_time = 0
        timer_beep_counter = 0
        cur.execute('SELECT message FROM messages ORDER BY id ASC LIMIT 1 OFFSET ?', (timer_beep_counter,))

        message = cur.fetchone()
        
    await context.bot.send_message(job.chat_id, text=message[0])

    timer_beep_counter += 1
    print(f"Beep! {job.data} seconds are over! This is beep number {timer_beep_counter}.")
    conn.close()

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
