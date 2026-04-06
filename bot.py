import os
import logging
import base64
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Railway-dagi o'zgaruvchilar
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)

def analyze_image_with_ai(image_bytes):
    try:
        # Rasmni AI tushunadigan matn (base64) shakliga o'tkazamiz
        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "meta-llama/llama-3.2-vision-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Ushbu rasmni o'zbek tilida juda batafsil tasvirlab ber va undagi barcha matnlarni o'qi."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
            },
        )
        data = response.json()
        
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        else:
            error_msg = data.get('error', {}).get('message', 'Noma\'lum API xatosi')
            return f"AI tahlilida xatolik: {error_msg}"
            
    except Exception as e:
        return f"Tizim xatosi: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! Men OpenRouter orqali ishlaydigan yordamchingizman.\n"
        "Menga rasm yuboring, men uni tasvirlab beraman."
    )

async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Rasm qabul qilindi, tahlil qilinmoqda...")
        
        # Telegramdan rasmni yuklab olish
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        image_bytes = await file.download_as_bytearray()
        
        # AI funksiyasini chaqirish
        result = analyze_image_with_ai(image_bytes)
        
        # Javobni yuborish (agar juda uzun bo'lsa, bo'lib yuboradi)
        if len(result) > 4000:
            for i in range(0, len(result), 4000):
                await update.message.reply_text(result[i:i+4000])
        else:
            await update.message.reply_text(result)
            
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text(f"Xatolik yuz berdi: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
    
    app.run_polling()
