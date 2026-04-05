import os
import io
import logging
import PIL.Image
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men ko'zi ojizlar uchun yordamchi botman.\n"
        "Menga rasm yuboring — men tasvirlab beraman!"
    )


async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")

        file = await context.bot.get_file(update.message.photo[-1].file_id)
        image_bytes = await file.download_as_bytearray()

        img = PIL.Image.open(io.BytesIO(bytes(image_bytes)))

        response = model.generate_content([
            "Ushbu rasmni O'ZBEK TILIDA batafsil tasvirla. Rasmdagi matnlarni o'qi.",
            img
        ])

        await update.message.reply_text(response.text)

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text(f"Xato: {e}")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Rasm yuboring, men tahlil qilaman.")


if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()
