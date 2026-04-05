import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Railway Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini API-ni sozlash
genai.configure(api_key=GEMINI_API_KEY)

# DIQQAT: Agar 'gemini-1.5-flash' 404 bersa, 'gemini-1.5-pro' ni yozib ko'ring
MODEL_NAME = 'gemini-1.5-flash'
model = genai.GenerativeModel(MODEL_NAME)

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Menga rasm yuboring, men uni o'zbek tilida tasvirlab beraman.")

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")

        # Rasmni yuklab olish
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()

        # Gemini formatiga o'tkazish
        image_contents = [
            {
                "mime_type": "image/jpeg",
                "data": bytes(image_bytes)
            },
            "Ushbu rasmni o'zbek tilida juda batafsil tasvirlab ber va matnlarni o'qi."
        ]

        # Tahlil so'rovi
        response = model.generate_content(image_contents)
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("Gemini javob qaytara olmadi.")

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text(f"Xatolik: {str(e)}")

if __name__ == '__main__':
    if TELEGRAM_TOKEN and GEMINI_API_KEY:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
        app.run_polling()
    else:
        print("XATO: Tokenlar topilmadi!")
