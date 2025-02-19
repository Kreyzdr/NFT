import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import requests


# Токен и URL
API_TOKEN = '7941054212:AAFMoTj7ZxIfsKBQihcWIZmC6AOicAxrl94'
WEBAPP_URL = "https://1cf9-142-93-137-25.ngrok-free.app"

bot = telebot.TeleBot(API_TOKEN)


def set_persistent_menu_button(chat_id, telegram_id):
    """
    Устанавливает persistent menu button типа web_app для конкретного чата.
    URL кнопки включает параметр telegram_id для передачи в WebApp.
    """
    url = f"https://api.telegram.org/bot{API_TOKEN}/setChatMenuButton"
    payload = {
        "chat_id": chat_id,
        "menu_button": {
            "type": "web_app",
            "text": "Открыть приложение",
            "web_app": {
                "url": f"{WEBAPP_URL}?telegram_id={telegram_id}"
            }
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Обработчик команды /start:
      1. Получает telegram_id и username пользователя.
      2. Отправляет запрос к API для создания/обновления записи пользователя.
      3. Устанавливает persistent WebApp кнопку, которая появляется слева от поля ввода.
      4. Информирует пользователя о дальнейших действиях.
    """
    chat_id = message.chat.id
    # Используем id чата как telegram_id
    telegram_id = message.chat.id
    username = message.chat.username if message.chat.username else ""

    # Формируем URL API для создания/обновления пользователя в базе данных
    api_url = f"{WEBAPP_URL}/api/user?telegram_id={telegram_id}&username={username}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            bot.send_message(chat_id, "Ошибка при сохранении данных пользователя.")
    except Exception as e:
        bot.send_message(chat_id, "Ошибка при подключении к базе данных.")

    # создаём кнопку
    result = set_persistent_menu_button(chat_id, telegram_id)
    if not result.get("ok"):
        bot.send_message(chat_id, "Ошибка при установке кнопки приложения.")

    bot.send_message(
        chat_id,
        "Добро пожаловать! Нажмите на круглую кнопку слева от поля ввода, чтобы открыть приложение."
    )


bot.polling(non_stop=True)

