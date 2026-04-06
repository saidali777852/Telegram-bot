import os
import logging
import base64
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ENV o'zgaruvchilar - Railway Variables bo'limida bo'lishi shart
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)

def analyze_image_with_ai(image_bytes):
    try:
        # Rasmni AI tushunadigan base64 formatiga o'tkazish
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://railway.app", # Statistikalar uchun
                "X-Title": "Telegram Vision Bot"
            },
            json={
                "model": "openai/gpt-4o-mini", # Eng barqaror va aqlli model
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "Ushbu rasmni o'zbek tilida juda batafsil tasvirlab ber va undagi barcha matnlarni o'qib ber."
                            },
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

        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            return f"API xatolik berdi: {data.get('error', {}).get('message', 'Nomaʼlum xato')}"

    except Exception as e:
        return f"Tizim xatosi yuz berdi: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men rasmlarni tahlil qiluvchi botman. 📷\n"
        "Menga rasm yuboring, men uni tasvirlab beraman."
    )

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda... ⏳")

        # Telegram serveridan rasmni yuklab olish
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        image_bytes = await file.download_as_bytearray()

        # AI tahlilini olish
        result = analyze_image_with_ai(image_bytes)

        # Telegram xabar limiti (4096 belgi) uchun javobni bo'lib yuborish
        if len(result) > 4000:
            for i in range(0, len(result), 4000):
                await update.message.reply_text(result[i:i+4000])
        else:
            await update.message.reply_text(result)

    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text(f"Xatolik yuz berdi: {e}")

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
        print("XATO: Telegram Token yoki OpenRouter API Key topilmadi!")
    else:
        print("Bot ishga tushmoqda...")
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.PHOTO, analyze_image))

        app.run_polling()
