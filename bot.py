import os
import logging
import httpx
import base64
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men ko'zi ojizlar uchun yordamchi botman.\n\n"
        "Menga rasm yuboring — men tasvirlab beraman!\n"
        "Rasmdagi matnlarni ham o'qib beraman."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — Botni ishga tushirish\n"
        "/help — Yordam\n\n"
        "Rasm yuboring, men tahlil qilaman."
    )


async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Rasm tahlil qilinmoqda...")

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        async with httpx.AsyncClient() as client:
            response = await client.get(file.file_path)
            image_bytes = response.content

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

        prompt = """Sen ko'zi ojiz foydalanuvchilarga yordam beruvchi botsan.
Rasmni O'ZBEK TILIDA batafsil tasvirla:
1. Rasmda nima bor?
2. Muhim detallar
3. Rasmdagi matnlar (agar bo'lsa)
4. Ranglar
Oddiy va tushunarli tilda yoz."""

        payload = {
            "contents": [{
                "parts": [
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_base64}},
                    {"text": prompt}
                ]
            }],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1500}
        }

        async with httpx.AsyncClient(timeout=60) as client:
            res = await client.post(url, json=payload)
            res.raise_for_status()
            data = res.json()

        answer = data["candidates"][0]["content"]["parts"][0]["text"]

        if len(answer) > 4000:
            for i in range(0, len(answer), 4000):
                await update.message.reply_text(answer[i:i+4000])
        else:
            await update.message.reply_text(answer)

    except Exception as e:
        logger.error(f"Xato: {e}")
        await update.message.reply_text("Xatolik yuz berdi. Qayta urinib ko'ring.")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Rasm yuboring, men tahlil qilaman.")


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    logger.info("Bot ishga tushdi!")
    app.run_polling()


if __name__ == "__main__":
    main()
