import logging
import csv
import pandas as pd
import time
from pathlib import Path
from keys import token
from telegram import __version__ as TG_VER
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import undetected_chromedriver as uc
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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

timer_beep_counter = 0
csv_path = Path(r"C:\Users\evanb\git\AI\NEWFILES\OBEYORDIE\outputawesome.csv")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hi! Use /set <seconds> to set a timer")

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    global timer_beep_counter

    with csv_path.open('r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        for _ in range(timer_beep_counter):
            next(reader)
        message = next(reader)[0]

    await context.bot.send_message(job.chat_id, text=message)

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
        await update.effective_message.reply_text("Usage: /set <seconds>")

async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)

def scrape_telegram_channel():
    options = uc.ChromeOptions()
    options.add_argument('--disable-extensions')
    driver = uc.Chrome(options=options)
    driver.get('https://web.telegram.org/')
    input("Press Enter after you have logged in...")
    input("Press Enter after you have navigated to the channel...")

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'messages-container')))
    except TimeoutException:
        print("Loading took too much time!")

    messages_list = []
    while True:
        message_groups = driver.find_elements(By.XPATH, '//div[@class="message-date-group"]')
        for group in message_groups:
            messages = group.find_elements(By.XPATH, './/div[starts-with(@class, "message")]')
            for i in range(len(messages)):
                try:
                    message = group.find_elements(By.XPATH, './/div[starts-with(@class, "message")]')[i]
                    subtexts = message.text.split()
                    messages_list.append(subtexts)
                except StaleElementReferenceException:
                    messages_list.append(["Error Reading Data"])

        df = pd.DataFrame(messages_list)
        df = df.drop_duplicates()
        df = df.dropna(how='all')
        df.to_csv(csv_path, index=False, header=False)
        time.sleep(5)

def main() -> None:
    loop = asyncio.get_event_loop()
    scrape_task = loop.run_in_executor(None, scrape_telegram_channel)

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    loop.run_until_complete(application.run_polling())

if __name__ == "__main__":
    main()
