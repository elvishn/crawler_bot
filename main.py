import os
import pandas as pd
from io import BytesIO
from tabulate import tabulate
from telegram.helpers import escape_markdown
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
    if not context.user_data.get('waiting_for_file'):
        await update.message.reply_text('Сначала нажмите кнопку "Загрузить файл"!')
        return

    try:
        # Получение и сохранение файла
        document = update.message.document
        file = await document.get_file()
        file_path = os.path.join(UPLOADS_DIR, sanitize_filename(document.file_name))
        await file.download_to_drive(file_path)

        # Обработка данных
        df = pd.read_excel(file_path)

        # Валидация колонок
        required_columns = ['title', 'url', 'xpath']
        if not all(col in df.columns for col in required_columns):
            missing = set(required_columns) - set(df.columns)
            await update.message.reply_text(
                "Ошибка: отсутствуют колонки: " + ", ".join(missing),
                parse_mode=None
            )
            return

        # Очистка данных
        df = df.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        df.dropna(inplace=True)

        # Форматирование таблицы (без Markdown)
        table_text = tabulate(
            df[['title', 'xpath', 'url']],
            headers=['TITLE', 'XPATH', 'URL'],
            tablefmt='grid',
            stralign='center',
            numalign='center',
            showindex=False
        )

        # Формирование сообщения (без Markdown)
        message = (
            "ДАННЫЕ УСПЕШНО ЗАГРУЖЕНЫ\n\n"
            f"{table_text}\n\n"
            f"Всего записей: {len(df)}\n"
            f"Уникальных URL: {df['url'].nunique()}"
        )

        await update.message.reply_text(
            message,
            parse_mode=None  # Полностью отключаем Markdown
        )

    except Exception as e:
        await update.message.reply_text(
            f"Ошибка при обработке файла: {str(e)}",
            parse_mode=None
        )


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
