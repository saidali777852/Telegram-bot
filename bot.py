import os
import io
import base64
import logging
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men ko'zi ojizlar uchun yordamchi botman.\n"
        "Menga rasm yuboring — men o'zbek tilida tasvirlab beraman!"
    )


async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")

        file = await context.bot.get_file(update.message.photo[-1].file_id)
        image_bytes = await file.download_as_bytearray()

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(
                    data=bytes(image_bytes),
                    mime_type="image/jpeg"
                ),
                "Ushbu rasmni O'ZBEK TILIDA batafsil tasvirla. Rasmdagi matnlarni o'qi."
            ]
        )

        answer = response.text
        if len(answer) > 4000:
            for i in range(0, len(answer), 4000):
                await update.message.reply_text(answer[i:i+4000])
        else:
            await update.message.reply_text(answer)

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
