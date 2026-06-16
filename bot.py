import logging
import requests
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import Update

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

#Токены и ключи
TELEGRAM_TOKEN = "8921394203:AAER6Cn5TaT99h0Itv2xyi0HJ6gRRYzTnTQ" #Токен
EXCHANGE_API_KEY = "327eaf57dc67130fc1b50ae0" #ExchangeRate-API

#Основные валюты
COMMON_CURRENCIES = {
    'RUB': '🇷🇺 Российский Рубль',
    'USD': '🇺🇸 Доллар США',
    'EUR': '🇪🇺 Евро',
    'GBP': '🇬🇧 Фунт Стерлингов',
    'JPY': '🇯🇵 Японская Иена',
    'CNY': '🇨🇳 Китайский Юань',
}

class CurrencyBot:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"
        self.free_url = "https://api.exchangerate-api.com/v4/latest/"
    
    def get_exchange_rate(self, from_currency, to_currency):
        #Поиск курса валют
        try:
            response = requests.get(f"{self.free_url}{from_currency}")
            
            if response.status_code == 200:
                data = response.json()
                rate = data['rates'].get(to_currency)
                if rate:
                    return rate, data.get('date', 'N/A')
                else:
                    return None, None
            else:
                logger.error(f"Ошибка: {response.status_code}")
                return None, None
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            return None, None
    
    def convert_currency(self, amount, from_curr, to_curr):
        #Обмен валют
        rate, date = self.get_exchange_rate(from_curr, to_curr)
        if rate:
            converted = amount * rate
            return converted, rate, date
        return None, None, None

#Подключение сайта
currency_bot = CurrencyBot(EXCHANGE_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Стартовый экран (команда start)
    welcome_text = """
*Этот бот может обменять любую валюту на другую и подсказать её курс*

Он может:
• Проверять курсы валют в реальном времени
• Обменивать любую валюту на другую

*Доступные команды:*
/rate - Проверка курса между двумя валютами
/convert - Обмен любого количества одной валюты на другую
/supported - Выдаёт список всех доступных валют
/help - Открывает список команд

    """
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Команда help
    help_text = """
*Доступные команды:*

/start - Запускает бота

/rate <что> <на что> - Выдаёт курс валют
Пример: `/rate RUB USD`

/convert <количество> <чего> <на что> - Обменивает валюты
Пример: `/convert 10 USD RUB`

/supported - Выдаёт список всех доступных валют

*Заметки:*
• У всех валют есть код из трёх букв (RUB, USD ...)
• Курс валют взят из ExchangeRate-API
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def rate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Команда курс валюты (rate)
    args = context.args
    
    if len(args) != 2:
        await update.message.reply_text(
            "*Неправильно, надо так:* `/rate <что> <на что>`\n"
            "Пример: `/rate RUB USD`",
            parse_mode='Markdown'
        )
        return
    
    from_curr = args[0].upper()
    to_curr = args[1].upper()
    
    await update.message.chat.send_action(action="typing")
    
    rate, date = currency_bot.get_exchange_rate(from_curr, to_curr)
    
    if rate:
        response = (
            f"*Обменный курс*\n\n"
            f"1 {from_curr} = {rate:.4f} {to_curr}\n\n"
            f"📅 *Дата:* {date}\n"
        )
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"❌ *Ошибка:* Не найдено курса валют между {from_curr} и {to_curr}\n\n"
            f"Напишите /supported для просмотра основных доступных валют",
            parse_mode='Markdown'
        )

async def convert_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Команда обмена валют (convert)
    args = context.args
    
    if len(args) != 3:
        await update.message.reply_text(
            "*Неправильно, надо так:* `/convert <кол-во> <чего> <на что>`\n"
            "Пример: `/convert 10 USD RUB`",
            parse_mode='Markdown'
        )
        return
    
    try:
        amount = float(args[0])
        from_curr = args[1].upper()
        to_curr = args[2].upper()
    except ValueError:
        await update.message.reply_text(
            "❌ *Ошибка:* Количество должно быть числом",
            parse_mode='Markdown'
        )
        return
    
    await update.message.chat.send_action(action="typing")
    
    converted, rate, date = currency_bot.convert_currency(amount, from_curr, to_curr)
    
    if converted:
        response = (
            f"*Обмен валюты*\n\n"
            f"{amount:,.2f} {from_curr} = {converted:,.2f} {to_curr}\n\n"
            f"📊 *Курс:* 1 {from_curr} = {rate:.4f} {to_curr}\n"
            f"📅 *Дата:* {date}\n\n"
        )
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"❌ *Ошибка:* Неверный код {from_curr} или {to_curr}\n\n"
            f"Напишите /supported для просмотра основных доступных валют",
            parse_mode='Markdown'
        )

async def supported_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Команда валют (supported)
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        if response.status_code == 200:
            data = response.json()
            currencies = list(data['rates'].keys())
            
            response_text = "*Команда /supported показывает валюты*\n\n"
            response_text += "Основные валюты:\n"
            for code, name in list(COMMON_CURRENCIES.items())[:10]:
                response_text += f"• {code} - {name}\n"
            
            response_text += f"\n*Всего:* {len(currencies)} валют доступно\n"
            response_text += "\nИспользуйте код из трёх заглавных латинских букв\n"
            response_text += "Пример: USD, RUB, EUR ..."
            
            await update.message.reply_text(response_text, parse_mode='Markdown')
        else:
            await update.message.reply_text("Извините, но сайт с валютами не работает")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip().upper()
    
    if not query:
        return
    
    parts = query.split()
    
    results = []
    
    try:
        if len(parts) == 3 and parts[0].replace('.', '').isdigit():
            amount = float(parts[0])
            from_curr = parts[1]
            to_curr = parts[2]
            converted, rate, date = currency_bot.convert_currency(amount, from_curr, to_curr)
            
            if converted:
                from telegram import InlineQueryResultArticle, InputTextMessageContent
                result = InlineQueryResultArticle(
                    id="1",
                    title=f"{amount} {from_curr} to {to_curr}",
                    description=f"{converted:.2f} {to_curr} (Rate: {rate:.4f})",
                    input_message_content=InputTextMessageContent(
                        f"*{amount:,.2f} {from_curr}* = *{converted:,.2f} {to_curr}*\n"
                        f"📊 Курс: 1 {from_curr} = {rate:.4f} {to_curr}"
                    )
                )
                results.append(result)
        
        elif len(parts) == 2:
            from_curr, to_curr = parts
            rate, date = currency_bot.get_exchange_rate(from_curr, to_curr)
            
            if rate:
                from telegram import InlineQueryResultArticle, InputTextMessageContent
                result = InlineQueryResultArticle(
                    id="1",
                    title=f"1 {from_curr} to {to_curr}",
                    description=f"1 {from_curr} = {rate:.4f} {to_curr}",
                    input_message_content=InputTextMessageContent(
                        f"*1 {from_curr}* = *{rate:.4f} {to_curr}*\n"
                        f"📅 Дата: {date}"
                    )
                )
                results.append(result)
    
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    
    await update.inline_query.answer(results)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ *Ошибка*\n"
            "Попробуйте повторить свой запрос позже",
            parse_mode='Markdown'
        )

def main():
    #Создание бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    #Подключение комманд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rate", rate_command))
    application.add_handler(CommandHandler("convert", convert_command))
    application.add_handler(CommandHandler("supported", supported_command))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: inline_query_handler(u, c)))
    
    application.add_error_handler(error_handler)
    
    #Включение бота
    print("Включаем бота")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()