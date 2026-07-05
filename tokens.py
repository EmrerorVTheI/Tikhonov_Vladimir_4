import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Достаем переменные окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
EXCHANGE_API_KEY = os.getenv('EXCHANGE_API_KEY')

# Проверяем, что переменные загружены
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не найден в переменных окружения")
if not EXCHANGE_API_KEY:
    raise ValueError("EXCHANGE_API_KEY не найден в переменных окружения")

# Используем переменные
print(f"TELEGRAM_TOKEN: {TELEGRAM_TOKEN[:10]}...")  # показываем только первые 10 символов для безопасности
print(f"EXCHANGE_API_KEY: {EXCHANGE_API_KEY[:10]}...")