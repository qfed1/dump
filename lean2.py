import logging
import sqlite3
import asyncio
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from collections import defaultdict

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

token = "your-token-here"  # Replace with your token
timer_beep_counter = int(input("Enter a starting beep counter: "))
MAX_MESSAGE_LENGTH = 4030

last_refresh_time = 0
db_path = 'filter_gold.db'  # Path to the SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create a dictionary to store the count of warnings for each job
job_warnings = defaultdict(int)

async def start(update: Update, context: CallbackContext) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! Use /set <seconds> to set a timer")

async def alarm(context: CallbackContext) -> None:
    global timer_beep_counter
    job = context.job

    if job_warnings[job.name] >= 5:
        # Skip this execution if we've had 5 warnings in a row
        return

    # Rest of your alarm code...

def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_timer(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    try:
        due = float(context.args[0])
        if due < 0:
            await context.bot.send_message(chat_id=chat_id, text="Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(alarm, due, context=context, name=str(chat_id))

        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        await context.bot.send_message(chat_id=chat_id, text=text)

    except (IndexError, ValueError):
        await context.bot.send_message(chat_id=chat_id, text="Usage: /set <seconds> DO NOT SET LOWER THAN 0.43 SECONDS UNDER NO CIRCUMSTANCES!!!")

async def unset(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await context.bot.send_message(chat_id=chat_id, text=text)

def main() -> None:
    bot = Bot(token)
    update_queue = asyncio.Queue()
    updater = Updater(bot, update_queue)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler(["start", "help"], start))
    dp.add_handler(CommandHandler("set", set_timer))
    dp.add_handler(CommandHandler("unset", unset))

    asyncio.run(updater.start_polling())

if __name__ == "__main__":
    main()
