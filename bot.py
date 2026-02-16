import os
from datetime import datetime, timedelta
from collections import defaultdict

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ====== DATA STORAGE (просте, в памʼяті) ======
user_data = defaultdict(lambda: {
    "streak": 0,
    "last_training": None,
    "total_trainings": 0,
    "total_rounds": 0,
})

# ====== PLANS ======
PLANS = {
    0: ["Присідання x20", "Планка 1 хв", "Віджимання x15"],
    1: ["Біг на місці 5 хв", "Прес x25"],
    2: ["Присідання x30", "Планка 2 хв"],
    3: ["Легкий день 🧘"],
    4: ["Віджимання x20", "Прес x30"],
    5: ["Кардіо 10 хв"],
    6: ["Відновлення 💤"],
}

# ====== KEYBOARD ======
KEYBOARD = ReplyKeyboardMarkup(
    [
        ["▶️ Почати тренування"],
        ["⏰ Нагадати через 10 хв", "⏱ Почати раніше"],
        ["📅 План на сьогодні", "📋 Перелік вправ"],
        ["🔥 Streak", "📊 Статистика"],
        ["🥇 Досягнення"],
    ],
    resize_keyboard=True
)

# ====== START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏋️‍♂️ Я твій тренер!\n\n"
        "⏰ Нагадую щодня о 21:30\n"
        "💪 Відмічай тренування і збирай streak\n\n"
        "👇 Обери дію кнопками",
        reply_markup=KEYBOARD
    )

# ====== TRAINING ======
async def start_training(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 Тренування почалось!\n"
        "Після завершення напиши, скільки кіл зробив (число)."
    )

# ====== REMIND 10 MIN ======
async def remind_10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏰ Добре, нагадаю через 10 хв!")
    context.job_queue.run_once(
        reminder_job,
        when=600,
        chat_id=update.effective_chat.id,
    )

async def reminder_job(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="⏰ Нагадую! Час тренуватись 💪",
        reply_markup=KEYBOARD
    )

# ====== EARLY START ======
async def early_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏱ Починаємо раніше — вперед 💪")
    await start_training(update, context)

# ====== PLAN ======
async def today_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = datetime.now().weekday()
    plan = "\n".join(PLANS.get(day, []))
    await update.message.reply_text(f"📅 План на сьогодні:\n{plan}")

# ====== EXERCISES ======
async def exercises(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 Перелік вправ:\n"
        "• Присідання\n"
        "• Віджимання\n"
        "• Планка\n"
        "• Прес\n"
        "• Кардіо\n"
    )
    await update.message.reply_text(text)

# ====== STREAK ======
async def streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = user_data[update.effective_user.id]
    await update.message.reply_text(f"🔥 Твій streak: {data['streak']} днів")

# ====== STATS ======
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = user_data[update.effective_user.id]
    await update.message.reply_text(
        f"📊 Статистика:\n"
        f"🏋️ Тренувань: {data['total_trainings']}\n"
        f"🔄 Кіл: {data['total_rounds']}"
    )

# ====== ACHIEVEMENTS ======
async def achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = user_data[update.effective_user.id]
    ach = []
    if data["total_trainings"] >= 1:
        ach.append("🥉 Перше тренування")
    if data["streak"] >= 5:
        ach.append("🥈 5 днів без пропусків")
    if data["total_rounds"] >= 50:
        ach.append("🥇 50 кіл")

    await update.message.reply_text(
        "🥇 Досягнення:\n" + ("\n".join(ach) if ach else "Поки немає 😌")
    )

# ====== HANDLE NUMBERS ======
async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        return

    rounds = int(update.message.text)
    uid = update.effective_user.id
    data = user_data[uid]

    today = datetime.now().date()
    if data["last_training"] != today:
        data["streak"] += 1
        data["total_trainings"] += 1
        data["last_training"] = today

    data["total_rounds"] += rounds

    await update.message.reply_text(
        f"✅ Записав {rounds} кіл!\n🔥 Streak: {data['streak']}",
        reply_markup=KEYBOARD
    )

# ====== MAIN ======
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^▶️"), start_training))
    app.add_handler(MessageHandler(filters.Regex("^⏰"), remind_10))
    app.add_handler(MessageHandler(filters.Regex("^⏱"), early_start))
    app.add_handler(MessageHandler(filters.Regex("^📅"), today_plan))
    app.add_handler(MessageHandler(filters.Regex("^📋"), exercises))
    app.add_handler(MessageHandler(filters.Regex("^🔥"), streak))
    app.add_handler(MessageHandler(filters.Regex("^📊"), stats))
    app.add_handler(MessageHandler(filters.Regex("^🥇"), achievements))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

    app.run_polling()

if __name__ == "__main__":
    main()

