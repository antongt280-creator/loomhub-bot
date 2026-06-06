import os
import threading
from datetime import datetime
import telebot
from telebot import types
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "LoomHub Server Active!"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

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
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

@bot.message_handler(commands=['start'])
def start_cmd(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🔑 Get Free Key"))
    markup.row(types.KeyboardButton("👤 Profile"))
    
    welcome_text = (
        "🤖 *Welcome to LoomHub Key Bot!*\n\n"
        f"⚠️ WARNING: To use this bot, you MUST be subscribed to our official Telegram channel: {CHANNEL_USERNAME}\n\n"
        "Please make sure you are subscribed, then use the menu below to get your 24h key or check your profile."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🔑 Get Free Key")
def get_key_msg(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        btn_link = types.InlineKeyboardButton("➡️ Subscribe to Channel", url=f"https://t.me{CHANNEL_USERNAME.lstrip('@')}")
        markup.add(btn_link)
        fail_text = (
            f"❌ *Access Denied!*\n\nYou are not subscribed to our channel {CHANNEL_USERNAME}.\n\n"
            f"You MUST subscribe to {CHANNEL_USERNAME} to unlock the bot! Click the button below to join, then try again."
        )
        bot.send_message(message.chat.id, fail_text, parse_mode="Markdown", reply_markup=markup)
        return

    daily_key = generate_daily_key()
    key_text = f"✅ *Key Generated Successfully!*\n\nYour key for today:\n`{daily_key}`\n\nTap to copy it. This key changes automatically every 24 hours. Paste it into the script GUI inside Roblox!"
    bot.send_message(message.chat.id, key_text, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "👤 Profile")
def profile_msg(message):
    profile_text = (
        f"👤 *Your LoomHub Profile:*\n\n"
        f"💰 Token Balance: *0*\n"
        f"👥 Friends Invited: *0*\n\n"
        f"_(Referral system is temporarily under maintenance)_"
    )
    bot.send_message(message.chat.id, profile_text, parse_mode="Markdown")

if __name__ == "__main__":
    t = threading.Thread(target=run_web_server)
    t.start()
    try:
        bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        pass
    bot.infinity_polling()
    
