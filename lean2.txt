from keys import token
import logging
import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
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

def fetch_message_after_wait(offset):
    cursor.execute('SELECT eth_address, message FROM filtereed_messages LIMIT 1 OFFSET ?', (offset,))
    return cursor.fetchone()

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hi! Use /set <seconds> to set a timer")

def alarm(context: CallbackContext) -> None:
    global timer_beep_counter
    global last_refresh_time
    job = context.job

    if job_warnings[job.name] >= 5:
        # Skip this execution if we've had 5 warnings in a row
        return

    cursor.execute('SELECT eth_address, message FROM filtered_messages LIMIT 1 OFFSET ?', (timer_beep_counter,))
    row = cursor.fetchone()
    if row is None:
        row = fetch_message_after_wait(timer_beep_counter)
        if row is None:
            last_refresh_time = 0
            cursor.execute('SELECT eth_address, message FROM filtered_messages LIMIT 1') 
            row = cursor.fetchone()

    eth_address, message_text = row if row else ("", "")

    # Replace the desired phrases
    if message_text.startswith("Token Update Name:"):
        message_text = "🪙 HYPE TOKEN UPDATE🚀" + message_text[19:]
    elif message_text == "New Token Found !!":
        message_text = "🪙 HYPE TOKEN APPROVED 🚀"

    message = f"Row {timer_beep_counter}: {eth_address} - {message_text}" if eth_address.strip() and message_text.strip() else "No more messages"

    try:
        if len(message) <= MAX_MESSAGE_LENGTH:
            context.bot.send_message(job.context, text=message)
        else:
            messages = [message[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(message), MAX_MESSAGE_LENGTH)]
            for i, msg in enumerate(messages, 1):
                context.bot.send_message(job.context, text=f"{msg}\n\nPart {i}/{len(messages)}")
    except Exception as e:
        print(e)
        job_warnings[job.name] += 1  # Increment the warning count for this job
    else:
        job_warnings[job.name] = 0  # Reset the count if we successfully sent a message

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

def main() -> None:
    updater = Updater(token)

    updater.dispatcher.add_handler(CommandHandler(["start", "help"], start))
    updater.dispatcher.add_handler(CommandHandler("set", set_timer))
    updater.dispatcher.add_handler(CommandHandler("unset", unset))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
