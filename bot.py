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

# 404 xatosini oldini olish uchun modelni to'liq nomi bilan chaqiramiz
model = genai.GenerativeModel('models/gemini-1.5-flash')

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Menga rasm yuboring, men uni o'zbek tilida tasvirlab beraman.")

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")

        # Rasmni yuklab olish
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()

        # Gemini-ga yuborish uchun ma'lumotlar
        prompt = "Ushbu rasmni o'zbek tilida batafsil tasvirlab ber va matnlarni o'qi."
        image_data = {
            "mime_type": "image/jpeg",
            "data": bytes(image_bytes)
        }

        # Tahlil qilish
        response = model.generate_content([prompt, image_data])

        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("Gemini tushunarli javob qaytara olmadi.")

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text(f"Xatolik yuz berdi: {str(e)}")

if __name__ == '__main__':
    if TELEGRAM_TOKEN and GEMINI_API_KEY:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
        app.run_polling()
