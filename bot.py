import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# [span_0](start_span)Railway Variables bo'limidan ma'lumotlarni o'qiymiz[span_0](end_span)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# [span_1](start_span)Gemini API-ni sozlash[span_1](end_span)
genai.configure(api_key=GEMINI_API_KEY)

# 404 xatoligini oldini olish uchun eng barqaror model nomidan foydalanamiz
# Agar bu ham ishlamasa, 'gemini-1.5-pro' deb o'zgartirib ko'ring
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# [span_2](start_span)Loglarni sozlash[span_2](end_span)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    [span_3](start_span)"""Botni ishga tushirish xabari[span_3](end_span)"""
    await update.message.reply_text(
        "Salom! Men ko'zi ojizlar uchun yordamchi botman.\n"
        "Menga rasm yuboring — men uni o'zbek tilida tasvirlab beraman!"
    )

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    [span_4](start_span)"""Rasmni qabul qilish va Gemini orqali tahlil qilish[span_4](end_span)"""
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")

        # 1. [span_5](start_span)Eng yuqori sifatli rasmni yuklab olish[span_5](end_span)
        photo_file = await update.message.photo[-1].get_file()
        image_bytes = await photo_file.download_as_bytearray()

        # 2. Gemini uchun rasm formatini tayyorlash
        image_data = {
            "mime_type": "image/jpeg",
            "data": bytes(image_bytes)
        }
        
        # 3. [span_6](start_span)Prompt (ko'rsatma) berish[span_6](end_span)
        prompt = "Ushbu rasmni O'ZBEK TILIDA juda batafsil tasvirlab ber. Agar rasmdagi yozuvlar bo'lsa, ularni ham o'qib ber."

        # 4. Gemini-ga so'rov yuborish
        response = model.generate_content([prompt, image_data])

        # 5. [span_7](start_span)Javobni foydalanuvchiga yuborish[span_7](end_span)
        if response.text:
            await update.message.reply_text(response.text)
        else:
            await update.message.reply_text("Kechirasiz, rasm mazmunini aniqlay olmadim.")

    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {e}")
        await update.message.reply_text(f"Xatolik: {str(e)}")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    [span_8](start_span)"""Matnli xabarlar uchun javob[span_8](end_span)"""
    await update.message.reply_text("Iltimos, tahlil qilishim uchun rasm yuboring.")

if __name__ == '__main__':
    # [span_9](start_span)Tokenlar mavjudligini tekshirish[span_9](end_span)
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        logger.error("XATO: TELEGRAM_TOKEN yoki GEMINI_API_KEY topilmadi!")
    else:
        # [span_10](start_span)Botni qurish va handlerlarni qo'shish[span_10](end_span)
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
        
        logger.info("Bot muvaffaqiyatli ishga tushdi...")
        app.run_polling()
