import os
import logging
import httpx
import base64
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Railway'dagi Variables bo'limidan ma'lumotlarni o'qiymiz
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Xatoliklarni kuzatish uchun sozlama
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men ko'zi ojizlar uchun yordamchi botman.\n"
        "Menga rasm yuboring – men tasvirlab beraman!\n"
        "Rasmdagi matnlarni ham o'qib beraman."
    )

# /help komandasi
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start – Botni ishga tushirish\n"
        "/help – Yordam\n"
        "Rasm yuboring, men tahlil qilaman."
    )

# Rasmni qabul qilish va tahlil qilish (Soddalashtirilgan struktura)
async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not GEMINI_API_KEY:
        await update.message.reply_text("Xato: Gemini API kaliti sozlanmagan.")
        return

    await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")
    # Bu yerda rasm bilan ishlash kodingiz davom etadi...

if __name__ == '__main__':
    # Token mavjudligini tekshirish
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN topilmadi! Railway Variables bo'limini tekshiring.")
    else:
        # Botni ishga tushirish
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # Handlerlarni qo'shish
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.PHOTO, analyze_image))
        
        print("Bot ishga tushdi...")
        application.run_polling()
