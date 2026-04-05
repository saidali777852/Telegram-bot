import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Railway Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini-ni sozlash
genai.configure(api_key=GEMINI_API_KEY)

# 404 xatosini oldini olish uchun eng sodda nomdan foydalanamiz
model = genai.GenerativeModel('gemini-1.5-flash')

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Menga rasm yuboring, men uni tasvirlab beraman.")

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")
        
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        
        # Tasvir ma'lumotlarini formatlash
        image_data = {
            "mime_type": "image/jpeg",
            "data": bytes(image_bytes)
        }
        
        # So'rov yuborish
        response = model.generate_content([
            "Ushbu rasmni o'zbek tilida juda batafsil tasvirlab ber va matnlarni o'qi.",
            image_data
        ])
        
        await update.message.reply_text(response.text)
        
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        # Agar yana 404 bersa, bu API kalitingiz cheklovi bilan bog'liq bo'lishi mumkin
        await update.message.reply_text(f"Xatolik: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
    app.run_polling()
