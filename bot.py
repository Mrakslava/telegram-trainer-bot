import os
import json
from datetime import datetime, timedelta, time

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"

# ------------------ Дані ------------------

PLANS = {
    0: ["Віджимання – 20", "Присідання – 30", "Планка – 30 сек"],      # Пн
    1: ["Прес – 25", "Випади – 20", "Планка – 40 сек"],              # Вт
    2: ["Віджимання – 25", "Присідання – 40"],                       # Ср
    3: ["Прес – 30", "Планка – 45 сек"],                             # Чт
    4: ["Берпі – 15", "Присідання – 30"],                            # Пт
    5: ["Легке кардіо – 10 хв"],                                     # Сб
    6: ["Розтяжка 🧘‍♂️"],                                           # Нд
}

# ------------------ Утиліти ------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "streak": 0,
            "last_day": None,
            "done": 0,
            "achievements": []
        }
    return data[uid]

# ------------------ Меню ------------------

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Почати тренування", callback_data="start_now")],
        [InlineKeyboardButton("⏰ Нагадати через 10 хв", callback_data="remind_10")],
        [InlineKeyboardButton("📅 План на сьогодні", callback_data="today_plan")],
        [InlineKeyboardButton("🔥 Streak", callback_data="streak")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("🥇 Досягнення", callback_data="achievements")],
    ])

# ------------------ Команди ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💪 Бот працює і готовий до тренувань!\n\nОбери команду 👇",
        reply_markup=main_menu()
    )

# ------------------ Callback ------------------

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = load_data()
    user = get_user(data, query.from_user.id)

    if query.data == "start_now":
        await send_training(query, data, user)

    elif query.data == "remind_10":
        context.job_queue.run_once(
            reminder,
            when=10 * 60,
            chat_id=query.message.chat_id
        )
        await query.edit_message_text("⏰ Нагадаю через 10 хв!")

    elif query.data == "today_plan":
        await query.edit_message_text(get_today_plan())

    elif query.data == "streak":
        await query.edit_message_text(f"🔥 Твій streak: {user['streak']} днів")

    elif query.data == "stats":
        await query.edit_message_text(
            f"📊 Статистика:\n"
            f"✅ Виконано тренувань: {user['done']}\n"
            f"🔥 Streak: {user['streak']}"
        )

    elif query.data == "achievements":
        ach = user["achievements"] or ["Поки що немає 😅"]
        await query.edit_message_text("🥇 Досягнення:\n" + "\n".join(ach))

    save_data(data)

# ------------------ Тренування ------------------

def get_today_plan():
    weekday = datetime.now().weekday()
    exercises = PLANS.get(weekday, [])
    text = "📅 План на сьогодні:\n"
    for e in exercises:
        text += f"• {e}\n"
    return text

async def send_training(query, data, user):
    today = datetime.now().date().isoformat()

    if user["last_day"] == today:
        await query.edit_message_text("✅ Ти вже сьогодні тренувався!")
        return

    # streak
    if user["last_day"] == (datetime.now().date() - timedelta(days=1)).isoformat():
        user["streak"] += 1
    else:
        user["streak"] = 1

    user["last_day"] = today
    user["done"] += 1

    if user["streak"] == 7 and "7 днів 🔥" not in user["achievements"]:
        user["achievements"].append("7 днів 🔥")

    await query.edit_message_text(
        "🏋️ Тренування почалось!\n\n" + get_today_plan()
    )

# ------------------ Нагадування ------------------

async def reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="⏰ Час тренуватись! Натисни /start 💪"
    )

# ------------------ Авто 21:30 ------------------

async def auto_training(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="🕘 21:30! Час тренування 💪\nНатисни /start"
    )

# ------------------ Запуск ------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    # щодня о 21:30
    app.job_queue.run_daily(
        auto_training,
        time=time(21, 30)
    )

    print("🤖 Бот запущений")
    app.run_polling()

if __name__ == "__main__":
    main()
