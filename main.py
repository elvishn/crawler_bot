import os
from pathvalidate import sanitize_filename
from config import load_config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters

config = load_config()
UPLOADS_DIR = config.paths.uploads_dir

async def start(update: Update, context: CallbackContext):
    button = InlineKeyboardButton('Загрузить файл', callback_data="upload")
    keyboard = InlineKeyboardMarkup([[button]])
    await update.message.reply_text(
        'Отправьте Excel-файл с данными. Нажмите кнопку ниже:',
        reply_markup=keyboard
    )

async def click_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    context.user_data['waiting_for_file'] = True
    await query.edit_message_text('Отправьте Excel файл', reply_markup=None)

async def handle_document(update: Update, context: CallbackContext):
    if not context.user_data['waiting_for_file']:
        await update.message.reply_text('Сначала нажмите кнопку "Загрузить файл"!')
        return

    original_name = update.message.document.file_name
    safe_name = sanitize_filename(original_name)
    file_path = os.path.join(UPLOADS_DIR, safe_name)

    file = await update.message.document.get_file()
    await file.download_to_drive(file_path)
    await update.message.reply_text('Файл сохранен!')


def main():
    app = Application.builder().token(config.tg_bot.token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CallbackQueryHandler(click_button))
    app.add_handler(MessageHandler(
        filters.Document.FileExtension("xlsx"),
        handle_document

    ))
    app.run_polling()

if __name__ == '__main__':
    main()
