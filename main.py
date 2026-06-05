import os
import hashlib
from datetime import datetime
from flask import Flask, request
import telebot
from telebot import types

app = Flask('')

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

CHANNEL_USERNAME = "@loompairik_scripts"

SCRIPTS_DATA = {
    "LoomHub Main": "SECRET_MAIN_SALT_123",
    "LoomHub Tycoon": "SECRET_TYCOON_SALT_456",
    "LoomHub Admin": "SECRET_ADMIN_SALT_789"
}

user_tokens = {}      
user_referrals = {}   
referred_by = {}      

@app.route('/', methods=['GET'])
def home():
    return "LoomHub Multi-Script Webhook Server Active!"

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

def generate_daily_key(salt):
    current_date = datetime.utcnow().strftime("%Y-%m-%d")
    raw_string = f"{current_date}_{salt}"
    hashed = hashlib.md5(raw_string.encode()).hexdigest().upper()
    return f"LOOM_{hashed[:8]}"

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
        inviter_id = int(args[1])
        if inviter_id != user_id and user_id not in referred_by and user_tokens[user_id] == 0:
            referred_by[user_id] = inviter_id
            if inviter_id in user_tokens:
                user_tokens[inviter_id] += 1
                user_referrals[inviter_id].append(user_id)
                try:
                    bot.send_message(inviter_id, "🎉 A new friend registered via your link! You received +1 Token.")
                except Exception:
                    pass

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("🔑 Get Key (Select Script)"))
    markup.row(types.KeyboardButton("👤 Profile / Referrals"))
    
    welcome_text = (
        "🤖 *Welcome to LoomHub Multi-Script Bot!*\n\n"
        f"To get keys for any of our scripts, you must be subscribed to our official channel: {CHANNEL_USERNAME}\n\n"
        "Use the menu below to get keys or check your referral balance."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🔑 Get Key (Select Script)")
def choose_script_msg(message):
    user_id = message.from_user.id
    
    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        btn_link = types.InlineKeyboardButton("➡️ Subscribe to Channel", url=f"https://t.me{CHANNEL_USERNAME.lstrip('@')}")
        markup.add(btn_link)
        
        fail_text = (
            f"❌ *Access Denied!*\n\nYou are not subscribed to our channel {CHANNEL_USERNAME}.\n\n"
            "Please click the button below to subscribe, then try again!"
        )
        bot.send_message(message.chat.id, fail_text, parse_mode="Markdown", reply_markup=markup)
        return

    markup = types.InlineKeyboardMarkup()
    for script_name in SCRIPTS_DATA.keys():
        btn = types.InlineKeyboardButton(script_name, callback_data=f"getkey_{script_name}")
        markup.add(btn)
        
    bot.send_message(message.chat.id, "⬇️ *Select the script you want to get a key for:*", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("getkey_"))
def send_script_key(call):
    user_id = call.from_user.id
    script_name = call.data.replace("getkey_", "")
    
    if not check_subscription(user_id):
        bot.answer_callback_query(call.id, "Error: You unsubscribed!")
        return
        
    salt = SCRIPTS_DATA.get(script_name, "DEFAULT")
    daily_key = generate_daily_key(salt)
    
    key_text = f"✅ *Key for {script_name}:*\n\n`{daily_key}`\n\nTap to copy it. This key changes automatically every 24 hours. Paste it into the script GUI inside Roblox!"
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=key_text, parse_mode="Markdown")
    bot.answer_callback_query(call.id, "Key generated successfully!")

@bot.message_handler(func=lambda msg: msg.text == "👤 Profile / Referrals")
def profile_msg(message):
    user_id = message.from_user.id
    tokens = user_tokens.get(user_id, 0)
    refs_count = len(user_referrals.get(user_id, []))
    bot_info = bot.get_me()
    ref_link = f"https://t.me{bot_info.username}?start={user_id}"
    
    profile_text = (
        f"👤 *Your LoomHub Profile:*\n\n"
        f"💰 Token Balance: *{tokens}*\n"
        f"👥 Friends Invited: *{refs_count}*\n\n"
        f"🔗 *Your Referral Link:* \n`{ref_link}`\n\n"
        f"_(Share this link with friends. You will get +1 Token for every friend who joins!)_"
    )
    bot.send_message(message.chat.id, profile_text, parse_mode="Markdown")

if __name__ == "__main__":
    bot.remove_webhook()
    render_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://onrender.com')
    bot.set_webhook(url=render_url + '/' + BOT_TOKEN)
    app.run(host='0.0.0.0', port=10000)
        
