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

# Modelni tanlash (Agar flash ishlamasa, 'gemini-1.5-pro' deb ko'ring)
model = genai.GenerativeModel('gemini-1.5-flash')

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Menga rasm yuboring — men o'zbek tilida tasvirlab beraman!")

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")

        # Rasmni yuklab olish
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        image_bytes = await file.download_as_bytearray()

        # Gemini-ga yuborish uchun ma'lumotlarni tayyorlash
        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": bytes(image_bytes)
            }
        ]
        
        prompt = "Ushbu rasmni O'ZBEK TILIDA juda batafsil tasvirla. Agar rasmdagi matnlar bo'lsa, ularni ham o'qib ber."

        # Tahlil qilish
        response = model.generate_content([prompt, image_parts[0]])

        await update.message.reply_text(response.text)

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        # Agar hali ham 404 bersa, model nomini 'gemini-pro-vision' ga o'zgartirib ko'ring
        await update.message.reply_text(f"Xatolik yuz berdi: {str(e)}")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        print("XATO: Tokenlar topilmadi! Railway Variables bo'limini tekshiring.")
    else:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
        app.run_polling()
