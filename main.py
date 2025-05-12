from config import load_config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext

config = load_config()

async def start(update: Update, context: CallbackContext):
    button = InlineKeyboardButton('Загрузить файл', callback_data="upload")
    keyboard = InlineKeyboardMarkup([[button]])
    await update.message.reply_text(
        'Отправьте Excel-файл с данными. Нажмите кнопку ниже:',
        reply_markup=keyboard
    )
def main():
    app = Application.builder().token(config.tg_bot.token).build()
    app.add_handler(CommandHandler('start', start))
    app.run_polling()

if __name__ == '__main__':
    main()
