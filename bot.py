import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Railway o'zgaruvchilari
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini API sozlamasi
genai.configure(api_key=GEMINI_API_KEY)

# Modelni tanlash - eng so'nggi va barqaror nom
model = genai.GenerativeModel('gemini-1.5-flash')

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Yangi API kaliti bilan bot tayyor.\n"
        "Menga rasm yuboring — men o'zbek tilida tasvirlab beraman!"
    )

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")

        # Rasmni yuklab olish
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()

        # Gemini uchun rasmni tayyorlash (eng xavfsiz usul)
        image_part = {
            "mime_type": "image/jpeg",
            "data": bytes(image_bytes)
        }

        # Tahlil so'rovi
        response = model.generate_content([
            "Ushbu rasmni o'zbek tilida juda batafsil tasvirlab ber va matnlarni o'qi.",
            image_part
        ])

        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("Kechirasiz, rasm mazmunini aniqlay olmadim.")

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        # Xatolikni aniq ko'rish uchun foydalanuvchiga yuboramiz
        await update.message.reply_text(f"Xatolik yuz berdi: {str(e)}")

if __name__ == '__main__':
    if TELEGRAM_TOKEN and GEMINI_API_KEY:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
        app.run_polling()
