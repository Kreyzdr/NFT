"БОт"

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import requests

from sekret_key.key import tg_token
# Токен вашего бота
API_TOKEN = f'{tg_token}'

bot = telebot.TeleBot(API_TOKEN)


WEBAPP_URL = "https://chat.qwenlm.ai/c/7f1974cb-1d15-4fd5-917b-000a23dad83b"
 # Укажите ваш домен или localhost


@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Получаем Telegram ID пользователя
    telegram_id = message.chat.id

    # Отправляем его в WebApp с параметром telegram_id
    url = f"{WEBAPP_URL}?telegram_id={telegram_id}"

    # Создаём клавиатуру с кнопкой
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    button = KeyboardButton(text="🎲 Roll Your Chance", web_app=WebAppInfo(url=url))
    markup.add(button)

    bot.send_message(message.chat.id, "Добро пожаловать! Нажмите кнопку ниже, чтобы открыть приложение.", reply_markup=markup)



# Запуск бота
bot.polling(non_stop=True)


