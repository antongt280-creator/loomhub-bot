import os
import threading
from flask import Flask
import telebot
from telebot import types

app = Flask('')

@app.route('/')
def home():
    return "LoomHub Сервер Активен!"

def run_web_server():
    app.run(host='0.0.0.0', port=10000)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

CHANNEL_USERNAME = "@loompairik_scripts"
CORRECT_KEY = "LOOM_FREE_ROT"

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_key = types.KeyboardButton("🔑 Получить бесплатный ключ")
    markup.add(btn_key)
    
    welcome_text = "🤖 Добро пожаловать в LoomHub Key Bot!\n\nДля получения суточного ключа нажмите кнопку ниже."
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🔑 Получить бесплатный ключ")
def get_key_msg(message):
    user_id = message.from_user.id
    
    if check_subscription(user_id):
        key_text = f"✅ Подписка подтверждена!\n\nТвой ключ на сегодня:\n`{CORRECT_KEY}`\n\nНажми на него, чтобы скопировать. Вставь его в LoomHub в игре!"
        bot.send_message(message.chat.id, key_text, parse_mode="Markdown")
    else:
        markup = types.InlineKeyboardMarkup()
        btn_link = types.InlineKeyboardButton("➡️ Подписаться на канал", url=f"https://t.me{CHANNEL_USERNAME.lstrip('@')}")
        markup.add(btn_link)
        
        fail_text = f"❌ Ошибка! Вы не подписаны на наш канал {CHANNEL_USERNAME}.\n\nПодпишитесь и повторите попытку!"
        bot.send_message(message.chat.id, fail_text, reply_markup=markup)

if __name__ == "__main__":
    t = threading.Thread(target=run_web_server)
    t.start()
    print("Бот успешно запущен в фоновом режиме веб-сервера!")
    bot.infinity_polling()
    
