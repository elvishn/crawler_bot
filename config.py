import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('BOT_TOKEN')
print("Токен:", token if token else "Не найден!")