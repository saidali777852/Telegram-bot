import os
import logging
import httpx
import base64
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- SOZLAMALAR ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Salom! Men ko'zi ojizlar uchun yaratilgan yordamchi botman.\n\n"
        "Menga rasm yuboring — men:\n"
        "• Rasmni batafsil tasvirlab beraman\n"
        "• Rasmdagi matnlarni o'qib beraman\n"
        "• Ranglar, odamlar, joylarni aniqlayman\n\n"
        "Rasm yuboring, men tayyor!"
    )
    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Yordam:\n\n"
        "/start — Botni qayta ishga tushirish\n"
        "/help — Ushbu yordam xabari\n\n"
        "Ishlash tartibi:\n"
        "1. Menga istalgan rasm yuboring\n"
        "2. Men rasmni tahlil qilaman\n"
        "3. Natijani matn shaklida yuboraman\n\n"
        "Savol va takliflar uchun bot yaratuvchisiga murojaat qiling."
    )
    await update.message.reply_text(text)


async def analyze_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Rasm tahlil qilinmoqda, biroz kuting...")

    try:
        # Rasmni yuklab olish
        photo = update.message.photo[-1]  # Eng yuqori sifatli rasm
        file = await context.bot.get_file(photo.file_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(file.file_path)
            image_bytes = response.content

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # Gemini API ga so'rov
        prompt = """Sen ko'zi ojiz foydalanuvchilarga yordam beruvchi AI yordamchisan.
        
Ushbu rasmni O'ZBEK TILIDA batafsil tasvirla:

1. UMUMIY TASVIR: Rasmda nima ko'rinmoqda? (qisqacha)
2. BATAFSIL: Rasmning har bir muhim qismini tushuntir
3. MATN: Agar rasmda yozuv/matn bo'lsa, ularni to'liq o'qi
4. RANGLAR: Asosiy ranglarni ayt
5. KAYFIYAT: Rasmning umumiy kayfiyati/muhiti qanday?

Javobni oddiy, tushunarli tilda yoz. Ko'zi ojiz inson uchun yozayotganingni esda tut."""

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1500
            }
        }

        async with httpx.AsyncClient(timeout=60) as client:
            api_response = await client.post(GEMINI_API_URL, json=payload)
            api_response.raise_for_status()
            result = api_response.json()

        # Javobni olish
        answer = result["candidates"][0]["content"]["parts"][0]["text"]
        
        # Uzun javoblarni bo'lib yuborish (Telegram 4096 belgi chegarasi)
        if len(answer) > 4000:
            parts = [answer[i:i+4000] for i in range(0, len(answer), 4000)]
            for part in parts:
                await update.message.reply_text(part)
        else:
            await update.message.reply_text(answer)

    except httpx.HTTPStatusError as e:
        logger.error(f"Gemini API xatosi: {e}")
        await update.message.reply_text(
            "Kechirasiz, rasm tahlil qilishda xatolik yuz berdi. "
            "Iltimos, qayta urinib ko'ring."
        )
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await update.message.reply_text(
            "Kutilmagan xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring."
        )


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Men faqat rasmlarni tahlil qila olaman. "
        "Iltimos, menga rasm yuboring."
    )


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, analyze_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))

    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
