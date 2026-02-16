import os
from datetime import datetime
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

# ===== DATA =====
user_data = defaultdict(lambda: {
    "streak": 0,
    "last_training": None,
    "total_trainings": 0,
    "total_rounds": 0,
})

# ===== DAYS =====
LIGHT_DAYS = [0, 3]  # Monday, Thursday

# ===== PLANS =====
POWER_PLAN = (
    "🔥 СИЛОВИЙ ДЕНЬ (5 кіл):\n"
    "• Присідання — 20 × 5\n"
    "• Віджимання — 15 × 5\n"
    "• Випади — 20 (10+10) × 5\n"
    "• Альпініст — 30 сек × 5\n"
    "• Планка — 40 сек × 5"
)

LIGHT_PLAN = (
    "🧘 ЛЕГКИЙ ДЕНЬ:\n"
    "• Присідання — 3 × 20\n"
    "• Віджимання — 3 × 12\n"
    "• Прес — 3 × 25\n"
    "• Планка — 3 × 1 хв"
)

# ===== KEYBOARD =====
KEYBOARD = ReplyKeyboardMarkup(
    [
        ["▶️ Почати тренування"],
        ["📅 План на сьогодні", "🗓 Календар тижня"],
        ["📋 Перелік вправ"],
        ["⏰ Нагадати через 10 хв", "⏱ Почати раніше"],
        ["🔥 Streak", "📊 Статистика"],
        ["🥇 Досягнення"],
    ],
    resize_keyboard=True
)

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏋️‍♂️ Я твій тренер.\n\n"
        "📅 План фіксований\n"
        "🔥 5 силових / 🧘 ПН + ЧТ легкі\n\n"
        "👇 Обирай дію кнопками",
        reply_markup=KEYBOARD
    )

# ===== TRAINING =====
async def start_training(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "▶️ Тренування почалось!\n"
        "Після завершення напиши, скільки **кіл** зробив (число)."
    )

# ===== PLAN TODAY =====
async def today_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = datetime.now().weekday()
    if day in LIGHT_DAYS:
        await update.message.reply_text(LIGHT_PLAN)
    else:
        await update.message.reply_text(POWER_PLAN)

# ===== WEEK CALENDAR =====
async def week_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🗓 КАЛЕНДАР ТИЖНЯ:\n\n"
        "Понеділок — 🧘 легкий\n"
        "Вівторок — 🔥 силовий\n"
        "Середа — 🔥 силовий\n"
        "Четвер — 🧘 легкий\n"
        "Пʼятниця — 🔥 силовий\n"
        "Субота — 🔥 силовий\n"
        "Неділя — 🔥 силовий"
    )

# ===== EXERCISES =====
async def exercises(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 ВПРАВИ:\n"
        "• Присідання\n"
        "• Віджимання\n"
        "• Випади\n"
        "• Альпініст\n"
        "• Планка\n"
        "• Прес"
    )

# ===== STREAK =====
async def streak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = user_data[update.effective_user.id]
    await update.message.reply_text(f"🔥 Streak: {d['streak']} днів")

# ===== STATS =====
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = user_data[update.effective_user.id]
    await update.message.reply_text(
        f"📊 Статистика:\n"
        f"🏋️ Тренувань: {d['total_trainings']}\n"
        f"🔄 Кіл: {d['total_rounds']}"
    )

# ===== ACHIEVEMENTS =====
async def achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = user_data[update.effective_user.id]
    ach = []
    if d["total_trainings"] >= 1:
        ach.append("🥉 Перше тренування")
    if d["streak"] >= 5:
        ach.append("🥈 5 днів підряд")
    if d["total_rounds"] >= 50:
        ach.append("🥇 50 кіл")

    await update.message.reply_text(
        "🥇 Досягнення:\n" + ("\n".join(ach) if ach else "Поки порожньо")
    )

# ===== REMIND 10 =====
async def remind_10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏰ Добре, нагадаю через 10 хв")

    context.job_queue.run_once(
        lambda ctx: ctx.bot.send_message(
            update.effective_chat.id,
            "⏰ Нагадування! Час тренування 💪",
            reply_markup=KEYBOARD
        ),
        600
    )

# ===== EARLY =====
async def early(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏱ Починаємо раніше 💪")
    await start_training(update, context)

# ===== NUMBERS =====
async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text.isdigit():
        return

    rounds = int(update.message.text)
    uid = update.effective_user.id
    d = user_data[uid]
    today = datetime.now().date()

    if d["last_training"] != today:
        d["streak"] += 1
        d["total_trainings"] += 1
        d["last_training"] = today

    d["total_rounds"] += rounds

    await update.message.reply_text(
        f"✅ Записав {rounds} кіл\n🔥 Streak: {d['streak']}",
        reply_markup=KEYBOARD
    )

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^▶️"), start_training))
    app.add_handler(MessageHandler(filters.Regex("^📅"), today_plan))
    app.add_handler(MessageHandler(filters.Regex("^🗓"), week_calendar))
    app.add_handler(MessageHandler(filters.Regex("^📋"), exercises))
    app.add_handler(MessageHandler(filters.Regex("^⏰"), remind_10))
    app.add_handler(MessageHandler(filters.Regex("^⏱"), early))
    app.add_handler(MessageHandler(filters.Regex("^🔥"), streak))
    app.add_handler(MessageHandler(filters.Regex("^📊"), stats))
    app.add_handler(MessageHandler(filters.Regex("^🥇"), achievements))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

    app.run_polling()

if __name__ == "__main__":
    main()
