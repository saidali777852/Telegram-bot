import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Railway Variables bo'limidan ma'lumotlarni olish
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini API-ni sozlash
genai.configure(api_key=GEMINI_API_KEY)

# Model nomi - eng so'nggi va barqaror versiya
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# Loglarni sozlash (xatolarni ko'rish uchun)
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot ishga tushganda salomlashish"""
    await update.message.reply_text("Salom! Menga rasm yuboring, men uni tasvirlab beraman.")

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rasmni qabul qilish va Gemini orqali tahlil qilish"""
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")

        # 1. Rasmni yuklab olish
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()

        # 2. Gemini uchun ma'lumotni tayyorlash
        image_data = {
            "mime_type": "image/jpeg",
            "data": bytes(image_bytes)
        }

        # 3. Gemini-ga so'rov yuborish
        response = model.generate_content([
            "Ushbu rasmni o'zbek tilida juda batafsil tasvirlab ber va rasmdagi matnlarni o'qib ber.",
            image_data
        ])

        # 4. Javobni foydalanuvchiga yuborish
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("Kechirasiz, rasm mazmunini aniqlay olmadim.")

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text(f"Xatolik yuz berdi: {str(e)}")

if __name__ == '__main__':
    # Botni ishga tushirish
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
    
    app.run_polling()
