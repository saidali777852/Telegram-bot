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

# Siz taklif qilgan yangi model nomi
model = genai.GenerativeModel('gemini-2.0-flash-exp')

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Gemini 2.0 modeli ishga tushdi. Rasm yuboring.")

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, Gemini 2.0 tahlil qilmoqda...")
        
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        
        # Rasm formati
        image_part = {
            "mime_type": "image/jpeg",
            "data": bytes(image_bytes)
        }
        
        # So'rov
        response = model.generate_content([
            "Ushbu rasmni o'zbek tilida juda batafsil tasvirlab ber va matnlarni o'qi.",
            image_part
        ])
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("Natija olinmadi.")
            
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text(f"Xatolik: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
    app.run_polling()
