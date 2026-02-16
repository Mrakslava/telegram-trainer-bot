import os
from telegram.ext import ApplicationBuilder, CommandHandler

# беремо токен з Environment Render
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update, context):
    await update.message.reply_text("✅ Бот працює! Готовий до тренувань 💪")

def main():
    if not BOT_TOKEN:
        raise RuntimeError("❌ BOT_TOKEN не знайдено в Environment")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("🤖 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
