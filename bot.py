import os
import logging
import base64
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ENV o'zgaruvchilar
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)

def analyze_image_with_ai(image_bytes):
    try:
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://your-app-name.com",  # shart emas, lekin yaxshi
                "X-Title": "Telegram Vision Bot"
            },
            json={
                "model": "openai/gpt-4o-mini",  # ✅ ISHLAYDIGAN MODEL
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Rasmni o'zbek tilida batafsil tasvirlab ber va undagi barcha matnlarni o'qib ber."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            }
        )

        data = response.json()

        # DEBUG uchun
        print("API RESPONSE:", data)

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"API xato: {data}"

    except Exception as e:
        return f"Tizim xatosi: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Menga rasm yuboring, men uni tahlil qilib beraman 📷"
    )

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")

        file = await context.bot.get_file(update.message.photo[-1].file_id)
        image_bytes = await file.download_as_bytearray()

        result = analyze_image_with_ai(image_bytes)

        # Uzun matnni bo‘lib yuborish
        for i in range(0, len(result), 4000):
            await update.message.reply_text(result[i:i+4000])

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text(f"Xatolik yuz berdi: {e}")

if __name__ == "__main__":
    print("Bot ishga tushyapti...")
    print("TOKEN bor:", TELEGRAM_TOKEN is not None)
    print("API KEY bor:", OPENROUTER_API_KEY is not None)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_image))

    app.run_polling()
