import os
import json
from datetime import datetime
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "results.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

async def start(update, context):
    await update.message.reply_text(
        "🏋️‍♂️ Я твій тренер!\n"
        "Щодня о 21:30 я нагадую про тренування.\n"
        "Після тренування просто напиши, скільки кіл зробив 💪"
    )

async def reminder(context):
    day = datetime.now().weekday()  # 0=пн
    if day in (0, 3):
        text = "🟢 ЛЕГКИЙ ДЕНЬ\n3×20 присідання\n3×12 віджимання\n3×25 прес\n3×1 хв планка"
    else:
        text = (
            "🔴 СИЛОВИЙ ДЕНЬ (5 кіл):\n"
            "20 присідань\n15 віджимань\n20 випадів\n30с альпініст\n40с планка"
        )

    await context.bot.send_message(chat_id=context.job.chat_id, text=text)

async def save_result(update, context):
    if not update.message.text.isdigit():
        return

    data = load_data()
    user = str(update.effective_user.id)
    date = datetime.now().strftime("%Y-%m-%d")

    data.setdefault(user, {})[date] = update.message.text
    save_data(data)

    await update.message.reply_text("✅ Записав результат! Так тримати 💪")

async def weekly_report(context):
    data = load_data()
    for user, records in data.items():
        total = sum(int(v) for v in records.values())
        await context.bot.send_message(
            chat_id=user,
            text=f"📊 Твій тижневий результат: {total} кіл 💥"
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_result))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(reminder, "cron", hour=21, minute=30, args=[app.bot])
    scheduler.add_job(weekly_report, "cron", day_of_week="mon", hour=9, args=[app.bot])
    scheduler.start()

    app.run_polling()

if __name__ == "__main__":
    main()
