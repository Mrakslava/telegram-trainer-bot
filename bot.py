from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.background import BackgroundScheduler

# 🔴 ВСТАВ СВІЙ ТОКЕН В ЛАПКАХ
BOT_TOKEN = "8254891256:AAHb5oka112LbU9axVv_R8gBRs1d2VSGMq0"

CHAT_ID = None
results = []

def day_type():
    wd = datetime.now().weekday()
    return "Легкий 🟢" if wd in (0, 3) else "Силовий 🔴"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    await update.message.reply_text(
        "🔥 Я тренер-бот.\n"
        "Пиши результат після тренування.\n"
        "Щодня о 21:30 я нагадую 💪"
    )

async def save_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    results.append({
        "date": datetime.now().strftime("%d.%m.%Y"),
        "type": day_type(),
        "result": text,
    })
    await update.message.reply_text("✅ Записав!")

async def reminder(app):
    if CHAT_ID:
        await app.bot.send_message(
            chat_id=CHAT_ID,
            text=f"🏋️ Тренування!\nТип: {day_type()}\n\nНапиши результат:"
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_result))

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: app.create_task(reminder(app)), "cron", hour=21, minute=30)
    scheduler.start()

    print("🤖 Бот запущений")
    app.run_polling()

if __name__ == "__main__":
    main()
