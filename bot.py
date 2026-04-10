import os
import json
import logging
import base64
import requests
from datetime import datetime, date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)

# === SOZLAMALAR ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DAILY_LIMIT = 20  # Kunlik rasm limiti

logging.basicConfig(level=logging.INFO)

# === MA'LUMOTLAR FAYLI ===
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": {}, "blocked": [], "total_images": 0}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, user_id):
    uid = str(user_id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "name": "",
            "total": 0,
            "today": 0,
            "today_date": str(date.today()),
            "joined": str(datetime.now())
        }
    u = data["users"][uid]
    if u["today_date"] != str(date.today()):
        u["today"] = 0
        u["today_date"] = str(date.today())
    return u

# === RASM XOTIRASI ===
user_images = {}  # {user_id: {"base64": ..., "history": [...]}}

# === AI FUNKSIYA ===
def ask_ai(messages):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://railway.app",
                "X-Title": "Telegram Vision Bot"
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": messages
            },
            timeout=30
        )
        data = response.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return f"Xato: {data.get('error', {}).get('message', 'Noma\'lum xato')}"
    except Exception as e:
        return f"Tizim xatosi: {str(e)}"

# === HANDLERLAR ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user = update.effective_user
    u = get_user(data, user.id)
    u["name"] = user.full_name
    save_data(data)

    await update.message.reply_text(
        f"Salom, {user.first_name}! 👋\n\n"
        "Men rasmlarni tahlil qiluvchi botman.\n\n"
        "📷 Rasm yuboring — men tasvirlab beraman\n"
        "💬 Keyin savol bering — men rasmni eslab turaman\n\n"
        "/help — yordam"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Buyruqlar:*\n\n"
        "📷 Rasm yuboring — tahlil qilaman\n"
        "💬 Savol yozing — rasm bo'yicha javob beraman\n"
        "/yangi — yangi suhbat boshlash\n"
        "/stat — mening statistikam\n"
        "/help — yordam",
        parse_mode="Markdown"
    )

async def stat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    u = get_user(data, update.effective_user.id)
    await update.message.reply_text(
        f"📊 *Sizning statistikangiz:*\n\n"
        f"Jami tahlil: {u['total']} ta rasm\n"
        f"Bugun: {u['today']}/{DAILY_LIMIT} ta\n"
        f"Qo'shilgan: {u['joined'][:10]}",
        parse_mode="Markdown"
    )

async def yangi_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_images:
        del user_images[user_id]
    await update.message.reply_text("✅ Yangi suhbat boshlandi. Rasm yuboring!")

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()

    if str(user.id) in [str(b) for b in data["blocked"]]:
        await update.message.reply_text("Siz bloklangansiz.")
        return

    u = get_user(data, user.id)
    u["name"] = user.full_name

    if u["today"] >= DAILY_LIMIT:
        await update.message.reply_text(
            f"❌ Kunlik limit ({DAILY_LIMIT} ta) tugadi. Ertaga qayta urinib ko'ring."
        )
        return

    await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda... ⏳")

    file = await context.bot.get_file(update.message.photo[-1].file_id)
    image_bytes = await file.download_as_bytearray()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Ushbu rasmni o'zbek tilida juda batafsil tasvirlab ber va undagi barcha matnlarni o'qib ber."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }
    ]

    result = ask_ai(messages)

    user_images[user.id] = {
        "base64": base64_image,
        "history": [
            {"role": "user", "content": [
                {"type": "text", "text": "Ushbu rasmni o'zbek tilida juda batafsil tasvirlab ber."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]},
            {"role": "assistant", "content": result}
        ]
    }

    u["total"] += 1
    u["today"] += 1
    data["total_images"] = data.get("total_images", 0) + 1
    save_data(data)

    if len(result) > 4000:
        for i in range(0, len(result), 4000):
            await update.message.reply_text(result[i:i+4000])
    else:
        await update.message.reply_text(result)

    await update.message.reply_text("💬 Endi rasm bo'yicha savol berishingiz mumkin!")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()

    if str(user.id) in [str(b) for b in data["blocked"]]:
        return

    if user.id not in user_images:
        await update.message.reply_text("📷 Avval rasm yuboring, keyin savol bering.")
        return

    savol = update.message.text
    img_data = user_images[user.id]

    img_data["history"].append({"role": "user", "content": savol})

    await update.message.reply_text("Javob tayyorlanmoqda... ⏳")
    result = ask_ai(img_data["history"])

    img_data["history"].append({"role": "assistant", "content": result})

    if len(result) > 4000:
        for i in range(0, len(result), 4000):
            await update.message.reply_text(result[i:i+4000])
    else:
        await update.message.reply_text(result)

# === ADMIN PANEL ===
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Ruxsat yo'q.")
        return

    data = load_data()
    keyboard = [
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stat")],
        [InlineKeyboardButton("👥 Foydalanuvchilar", callback_data="admin_users")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🚫 Bloklash", callback_data="admin_block")],
        [InlineKeyboardButton("✅ Blokdan chiqarish", callback_data="admin_unblock")],
    ]
    await update.message.reply_text(
        "👨‍💼 *Admin paneli*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    data = load_data()

    if query.data == "admin_stat":
        total_users = len(data["users"])
        total_images = data.get("total_images", 0)
        blocked = len(data["blocked"])
        today_active = sum(
            1 for u in data["users"].values()
            if u.get("today_date") == str(date.today()) and u.get("today", 0) > 0
        )
        await query.edit_message_text(
            f"📊 *Statistika:*\n\n"
            f"👥 Jami foydalanuvchilar: {total_users}\n"
            f"📷 Jami tahlil: {total_images}\n"
            f"🚫 Bloklangan: {blocked}\n"
            f"✅ Bugun faol: {today_active}",
            parse_mode="Markdown"
        )

    elif query.data == "admin_users":
        users_text = "👥 *Foydalanuvchilar:*\n\n"
        for uid, u in list(data["users"].items())[-10:]:
            users_text += f"• {u.get('name', 'Nomaʼlum')} (ID: {uid}) — {u.get('total', 0)} rasm\n"
        await query.edit_message_text(users_text, parse_mode="Markdown")

    elif query.data == "admin_broadcast":
        context.user_data["admin_action"] = "broadcast"
        await query.edit_message_text("📢 Broadcast xabarini yozing:")

    elif query.data == "admin_block":
        context.user_data["admin_action"] = "block"
        await query.edit_message_text("🚫 Bloklash uchun foydalanuvchi ID sini yozing:")

    elif query.data == "admin_unblock":
        context.user_data["admin_action"] = "unblock"
        await query.edit_message_text("✅ Blokdan chiqarish uchun ID yozing:")

async def admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    action = context.user_data.get("admin_action")
    if not action:
        return

    data = load_data()
    text = update.message.text

    if action == "broadcast":
        count = 0
        for uid in data["users"]:
            try:
                await context.bot.send_message(chat_id=int(uid), text=f"📢 {text}")
                count += 1
            except:
                pass
        context.user_data["admin_action"] = None
        await update.message.reply_text(f"✅ {count} ta foydalanuvchiga yuborildi.")

    elif action == "block":
        try:
            uid = int(text)
            if uid not in data["blocked"]:
                data["blocked"].append(uid)
                save_data(data)
            context.user_data["admin_action"] = None
            await update.message.reply_text(f"🚫 {uid} bloklandi.")
        except:
            await update.message.reply_text("ID noto'g'ri.")

    elif action == "unblock":
        try:
            uid = int(text)
            if uid in data["blocked"]:
                data["blocked"].remove(uid)
                save_data(data)
            context.user_data["admin_action"] = None
            await update.message.reply_text(f"✅ {uid} blokdan chiqarildi.")
        except:
            await update.message.reply_text("ID noto'g'ri.")

# === MAIN ===
if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
        print("XATO: TOKEN yoki API KEY topilmadi!")
    else:
        print("Bot ishga tushmoqda...")
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("stat", stat_command))
        app.add_handler(CommandHandler("yangi", yangi_command))
        app.add_handler(CommandHandler("admin", admin))
        app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
        app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            lambda u, c: admin_text(u, c) if u.effective_user.id == ADMIN_ID and c.user_data.get("admin_action") else text_handler(u, c)
        ))

        app.run_polling()
