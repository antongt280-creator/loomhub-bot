import os
import time
import secrets
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = '@loompairik_scripts' 
BOT_USERNAME = 'LoomHubKey_bot'

bot = Bot(token=API_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

users_db = {}

async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.KeyboardButton("🔑 Get Free Key"))
    keyboard.row(types.KeyboardButton("👤 My Profile & Referral"), types.KeyboardButton("⭐ Buy Premium (5 Tokens)"))
    return keyboard

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "User"
    
    if user_id not in users_db:
        users_db[user_id] = {'tokens': 0, 'last_key': None, 'key_time': 0, 'referred_by': None}
        
        args = message.get_args()
        if args and args.isdigit():
            referrer_id = int(args)
            if referrer_id in users_db and referrer_id != user_id:
                users_db[user_id]['referred_by'] = referrer_id
                users_db[referrer_id]['tokens'] += 1
                try:
                    await bot.send_message(referrer_id, f"🎉 Someone joined via your link! You received **+1 token**.")
                except:
                    pass

    await message.reply(f"Welcome, {username}! This is LoomHub Key Bot. Use the menu below to manage your keys.", reply_markup=get_main_keyboard())

@dp.message_handler(lambda message: message.text == "🔑 Get Free Key" or message.text == "/freekey")
async def free_key_handler(message: types.Message):
    user_id = message.from_user.id
    
    if not await is_user_subscribed(user_id):
        inline_kb = InlineKeyboardMarkup().add(InlineKeyboardButton("📢 Subscribe to Channel", url=f"https://t.me{CHANNEL_ID.replace('@', '')}"))
        await message.reply(f"❌ Access Denied! You must be subscribed to our channel to get a key.", reply_markup=inline_kb)
        return

    current_time = time.time()
    user_data = users_db.get(user_id, {'tokens': 0, 'last_key': None, 'key_time': 0})
    
    if user_data['last_key'] and (current_time - user_data['key_time']) < 86400:
        remaining = int(86400 - (current_time - user_data['key_time']))
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        await message.reply(f"⏳ Your key is still active. Next free key available in **{hours}h {minutes}m**.")
        return

    generated_key = f"LOOM_FREE_{secrets.token_hex(4).upper()}"
    if user_id not in users_db:
        users_db[user_id] = {'tokens': 0}
        
    users_db[user_id]['last_key'] = generated_key
    users_db[user_id]['key_time'] = current_time
    
    await message.reply(f"🔑 Your 24-hour key:\n\n`{generated_key}`\n\nCopy it and paste into your executor.")

@dp.message_handler(lambda message: message.text == "👤 My Profile & Referral")
async def profile_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id, {'tokens': 0})
    tokens = user_data.get('tokens', 0)
    ref_link = f"https://t.me{BOT_USERNAME}?start={user_id}"
    
    await message.reply(
        f"👤 **Your LoomHub Profile**\n\n"
        f"💰 Balance: **{tokens} tokens**\n\n"
        f"🔗 Your Referral Link (Get +1 token per friend):\n`{ref_link}`"
    )

@dp.message_handler(lambda message: message.text == "⭐ Buy Premium (5 Tokens)")
async def buy_premium_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = users_db.get(user_id, {'tokens': 0})
    
    if user_data.get('tokens', 0) < 5:
        await message.reply("❌ Not enough tokens! You need **5 tokens** for a Premium Key. Share your referral link to get more.")
        return
        
    users_db[user_id]['tokens'] -= 5
    premium_key = f"LOOM_PREM_{secrets.token_hex(6).upper()}"
    
    await message.reply(f"⭐ **Purchase successful!** 5 tokens deducted.\n\nYour Premium Key (30 Days):\n`{premium_key}`")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
        
