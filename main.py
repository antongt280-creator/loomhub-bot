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
    # Automatic port management for Render stability
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

CHANNEL_USERNAME = "@loompairik_scripts"
MULTIPLIER = 137

user_tokens = {}      
user_referrals = {}   
referred_by = {}      

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
    user_id = message.from_user.id
    
    if user_id not in user_tokens:
        user_tokens[user_id] = 0
        user_referrals[user_id] = []
    
    args = message.text.split()
    if len(args) > 1:
        try:
            inviter_id = int(args[0])
            if inviter_id != user_id and user_id not in referred_by and user_tokens[user_id] == 0:
                referred_by[user_id] = inviter_id
                if inviter_id in user_tokens:
                    user_tokens[inviter_id] += 1
                    user_referrals[inviter_id].append(user_id)
                    try:
                        bot.send_message(inviter_id, "🎉 A new friend registered via your link! You received +1 Token.")
                    except Exception:
                        pass
        except ValueError:
            pass

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🔑 Get Free Key"))
    markup.row(types.KeyboardButton("👤 Profile / Referrals"))
    
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
    key_text = f"✅ *Key Generated Successfully!*\n\nYour key for today:\n{daily_key}\n\nTap to copy it. This key changes automatically every 24 hours. Paste it into the script GUI inside Roblox!"
    bot.send_message(message.chat.id, key_text, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "👤 Profile / Referrals")
def profile_msg(message):
    user_id = message.from_user.id
    tokens = user_tokens.get(user_id, 0)

refs_count = len(user_referrals.get(user_id, []))
    
    try:
        bot_info = bot.get_me()
        ref_link = f"https://t.me{bot_info.username}?start={user_id}"
    except Exception:
        ref_link = "Error generating link. Try again later."
    
    profile_text = (
        f"👤 *Your LoomHub Profile:*\n\n"
        f"💰 Token Balance: *{tokens}*\n"
        f"👥 Friends Invited: *{refs_count}*\n\n"
        f"🔗 *Your Referral Link:* \n{ref_link}\n\n"
        f"_(Share this link with friends. You will get +1 Token for every friend who joins!)_"
    )
    bot.send_message(message.chat.id, profile_text, parse_mode="Markdown")

if name == "main":
    t = threading.Thread(target=run_web_server)
    t.start()
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling()
