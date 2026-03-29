from datetime import datetime
import random

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8477247508:AAHBAul8zBfNzsAQUsmx-W1ijnQN4IQg9sA"

motivations = [
    "Har kuni ozgina harakat ham katta natija beradi.",
    "Taslim bo‘lma, sen o‘ylagandan kuchliroqsan.",
    "Bugungi mehnat ertangi g‘alaba.",
    "Sekin bo‘lsa ham, oldinga yurish muhim.",
    "Katta natija sabr va intizom bilan keladi."
]


def get_main_keyboard():
    keyboard = [
        ["👋 Salom", "🕒 Vaqt"],
        ["📅 Sana", "💡 Motivatsiya"],
        ["🧮 Kalkulyator", "🌐 Kanal"],
        ["ℹ️ Yordam", "👤 Profil"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(
        f"Assalomu alaykum, {user}!\n\n"
        "Men sizning mukammallashtirilgan Telegram botingizman 🤖\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=get_main_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot buyruqlari:\n"
        "/start - botni ishga tushirish\n"
        "/help - yordam\n"
        "/about - bot haqida\n\n"
        "Yoki pastdagi tugmalardan foydalaning."
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bu bot Python va python-telegram-bot kutubxonasi yordamida yozilgan.\n"
        "VS Code ichida ishlash uchun mos."
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user

    if text == "👋 Salom":
        await update.message.reply_text(
            f"Salom, {user.first_name}! Yaxshimisiz?"
        )

    elif text == "🕒 Vaqt":
        now = datetime.now().strftime("%H:%M:%S")
        await update.message.reply_text(f"Hozirgi vaqt: {now}")

    elif text == "📅 Sana":
        today = datetime.now().strftime("%d-%m-%Y")
        await update.message.reply_text(f"Bugungi sana: {today}")

    elif text == "💡 Motivatsiya":
        await update.message.reply_text(random.choice(motivations))

    elif text == "👤 Profil":
        username = f"@{user.username}" if user.username else "Username yo‘q"
        await update.message.reply_text(
            f"Ism: {user.first_name}\n"
            f"Familiya: {user.last_name if user.last_name else 'yo‘q'}\n"
            f"Username: {username}\n"
            f"ID: {user.id}"
        )

    elif text == "🌐 Kanal":
        await update.message.reply_text(
            "Bu yerga o‘zingning kanal yoki guruh linkini qo‘yasan.\n"
            "Masalan:\n"
            "https://t.me/your_channel"
        )

    elif text == "ℹ️ Yordam":
        await help_command(update, context)

    elif text == "🧮 Kalkulyator":
        await update.message.reply_text(
            "Misol uchun shunday yozing:\n"
            "2+2\n"
            "10*5\n"
            "100/4"
        )

    else:
        try:
            result = eval(text, {"__builtins__": {}}, {})
            await update.message.reply_text(f"Natija: {result}")
        except:
            await update.message.reply_text(
                f"Siz yozdingiz: {text}\n"
                "Men bu xabarni tushunmadim."
            )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
