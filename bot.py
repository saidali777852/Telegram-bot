import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Railway Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini API-ni yangi standartda sozlash
genai.configure(api_key=GEMINI_API_KEY)

# DIQQAT: models/ prefiksini olib tashladik va eng barqaror versiyani tanladik
# Agar flash baribir ishlamasa, 'gemini-1.5-pro' ga o'zgartiring
model = genai.GenerativeModel('gemini-1.5-flash')

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Yangi sozlamalar bilan bot ishga tushdi. Rasm yuboring.")

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")
        
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()
        
        # Tasvir qismini alohida formatda tayyorlaymiz
        image_part = {
            "mime_type": "image/jpeg",
            "data": bytes(image_bytes)
        }
        
        # Muhim: generate_content ichida prompt va rasm ro'yxat ko'rinishida bo'lishi shart
        response = model.generate_content([
            "Ushbu rasmni o'zbek tilida batafsil tasvirlab ber.", 
            image_part
        ])
        
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("Gemini tahlil natijasini qaytarmadi.")
            
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        # Xatoni aniq ko'rish uchun botga yuboramiz
        await update.message.reply_text(f"Xatolik: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
    app.run_polling()
