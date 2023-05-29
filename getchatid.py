from keys import token
import logging
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    with open(f'{chat_id}.txt', 'w') as f:
        f.write(str(chat_id))
    await update.message.reply_text(f"Chat id {chat_id} saved to file.")

def main() -> None:
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("get_chat_id", get_chat_id))

    application.run_polling()

if __name__ == "__main__":
    main()
