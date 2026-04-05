import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Railway Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# API sozlamalari
genai.configure(api_key=GEMINI_API_KEY)

# DIQQAT: Agar flash yana 404 bersa, pastdagi nomni 'gemini-1.5-pro' qiling
model = genai.GenerativeModel('gemini-1.5-flash')

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Menga rasm yuboring, men tahlil qilaman.")

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")
        
        # Rasmni yuklab olish
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        
        # Gemini-ga yuborish uchun lug'at formatidan foydalanamiz
        image_part = {
            "mime_type": "image/jpeg",
            "data": bytes(image_bytes)
        }
        
        # So'rov yuborish (o'zbekcha prompt bilan)
        response = model.generate_content([
            "Ushbu rasmni o'zbek tilida juda batafsil tasvirlab ber va matnlarni o'qi.",
            image_part
        ])
        
        await update.message.reply_text(response.text)
        
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        error_msg = str(e)
        if "404" in error_msg:
            await update.message.reply_text("Xato: Model topilmadi. Pro versiyani sinab ko'ryapman...")
            # Agar flash ishlamasa, Pro-da urinib ko'rish mantiqi
        else:
            await update.message.reply_text(f"Xatolik: {error_msg}")

if __name__ == '__main__':
    if TELEGRAM_TOKEN and GEMINI_API_KEY:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
        app.run_polling()
