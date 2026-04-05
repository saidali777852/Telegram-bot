import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Railway Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini sozlamasi
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Menga rasm yuboring, men uni tahlil qilib beraman.")

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not GEMINI_API_KEY:
        await update.message.reply_text("Xato: Gemini API kaliti kiritilmagan.")
        return

    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")
        
        # Rasmni yuklab olish
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        image_bytes = await file.download_as_bytearray()
        
        # Gemini-ga yuborish
        contents = {
            "parts": [
                {"mime_type": "image/jpeg", "data": bytes(image_bytes)},
                {"text": "Ushbu rasmni batafsil tasvirlab ber va undagi yozuvlarni o'qib ber."}
            ]
        }
        
        response = model.generate_content(contents)
        await update.message.reply_text(response.text)
        
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text("Kechirasiz, rasmni tahlil qilishda xato yuz berdi.")

if __name__ == '__main__':
    if TELEGRAM_TOKEN:
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.PHOTO, analyze_image))
        application.run_polling()
