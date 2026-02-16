import os
from datetime import datetime, date, time
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

user_data = {}

keyboard = ReplyKeyboardMarkup(
    [
        ["📅 План на сьогодні", "📋 Перелік вправ"],
        ["⏰ Почати зараз", "🔥 Streak"],
        ["📊 Статистика", "🥇 Досягнення"],
    ],
    resize_keyboard=True,
)

def get_today_plan():
    weekday = datetime.now().weekday()  # 0=Mon
    if weekday in (0, 3):  # Monday, Thursday
        return (
            "🟡 ЛЕГКИЙ ДЕНЬ\n\n"
            "Присідання — 20 × 3\n"
            "Віджимання — 12 × 3\n"
            "Прес — 25 × 3\n"
            "Планка — 1 хв × 3"
        )
    else:
        return (
            "🟢 ОСНОВНЕ ТРЕНУВАННЯ (5 кіл)\n\n"
            "Присідання — 20 × 5\n"
            "Віджимання — 15 × 5\n"
            "Випади — 20 (10+10) × 5\n"
            "Альпініст — 30 сек × 5\n"
            "Планка — 40 сек × 5"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_data.setdefault(uid, {
        "streak": 0,
        "last_training": None,
        "trainings": 0
    })

    await update.message.reply_text(
        "🏋️‍♂️ Я твій тренер\n\n"
        "⏰ Нагадую щодня о 21:30\n"
        "💪 Натискай кнопки нижче",
        reply_markup=keyboard
    )

async def remind_2130(context: ContextTypes.DEFAULT_TYPE):
    for uid in user_data:
        await context.bot.send_message(
            chat_id=uid,
            text="⏰ 21:30 — ЧАС ТРЕНУВАННЯ 💪\n\n" + get_today_plan(),
            reply_markup=keyboard
        )

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = update.effective_user.id
    user_data.setdefault(uid, {
        "streak": 0,
        "last_training": None,
        "trainings": 0
    })

    if text == "📅 План на сьогодні":
        await update.message.reply_text(get_today_plan())

    elif text == "📋 Перелік вправ":
        await update.message.reply_text(
            "📋 Вправи:\n"
            "• Присідання\n"
            "• Віджимання\n"
            "• Випади\n"
            "• Альпініст\n"
            "• Планка\n"
            "• Прес"
        )

    elif text == "⏰ Почати зараз":
        today = date.today()
        last = user_data[uid]["last_training"]

        if last != today:
            if last == today.replace(day=today.day - 1):
                user_data[uid]["streak"] += 1
            else:
                user_data[uid]["streak"] = 1

            user_data[uid]["last_training"] = today
            user_data[uid]["trainings"] += 1

        await update.message.reply_text(
            "🔥 Тренування зараховано!\n\n" + get_today_plan()
        )

    elif text == "🔥 Streak":
        await update.message.reply_text(
            f"🔥 Серія: {user_data[uid]['streak']} днів"
        )

    elif text == "📊 Статистика":
        await update.message.reply_text(
            f"📊 Тренувань: {user_data[uid]['trainings']}"
        )

    elif text == "🥇 Досягнення":
        msg = "🥇 Досягнення:\n"
        if user_data[uid]["trainings"] >= 1:
            msg += "🥉 Перше тренування\n"
        if user_data[uid]["streak"] >= 5:
            msg += "🥈 5 днів без пропусків\n"
        await update.message.reply_text(msg)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    app.job_queue.run_daily(
        remind_2130,
        time=time(hour=21, minute=30)
    )

    app.run_polling()

if __name__ == "__main__":
    main()
