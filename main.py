import os
from datetime import datetime
from flask import Flask, request
import telebot
from telebot import types

app = Flask('')

@app.route('/')
def home():
    return "LoomHub Server Active!"

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

RENDER_URL = "https://onrender.com"
CHANNEL_USERNAME = "@loompairik_scripts"
MULTIPLIER = 137

def generate_daily_key():
    current_date = datetime.utcnow().strftime("%Y%m%d")
    seed = sum(ord(char) for char in current_date)
    result_num = (seed * MULTIPLIER) + 54321
    hashed_part = hex(result_num)[2:].upper()
    return f"LOOM_{hashed_part[:6]}"

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🔑 Get Free Key"))
    
    welcome_text = (
        "🤖 *Welcome to LoomHub Key Bot!*\n\n"
        f"⚠️ WARNING: You MUST be subscribed to: {CHANNEL_USERNAME}\n\n"
        "Click the button below to get your 24h key for Roblox script."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🔑 Get Free Key")
def get_key_msg(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        btn_link = types.InlineKeyboardButton("➡️ Subscribe to Channel", url=f"https://t.me{CHANNEL_USERNAME.lstrip('@')}")
        markup.add(btn_link)
        
        fail_text = f"❌ *Access Denied!*\n\nYou MUST subscribe to {CHANNEL_USERNAME} to unlock the bot!"
        bot.send_message(message.chat.id, fail_text, parse_mode="Markdown", reply_markup=markup)
        return

    daily_key = generate_daily_key()
    key_text = f"✅ *Key Generated!*\n\nYour key for today:\n`{daily_key}`\n\nPaste it into the script GUI inside Roblox!"
    bot.send_message(message.chat.id, key_text, parse_mode="Markdown")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_URL + '/' + BOT_TOKEN)
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
    
