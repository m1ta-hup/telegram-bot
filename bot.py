import os
import sqlite3
from datetime import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("8477247508:AAHBAul8zBfNzsAQUsmx-W1ijnQN4IQg9sA")

# O'ZGARTIRISH KERAK
ADMIN_ID = 6355362497  # bu yerga o'zingni telegram id'ingni yoz
CHANNEL_USERNAME = "@your_channel"  # bu yerga kanalingni yoz

DB_NAME = "bot.db"


# =========================
# DATABASE
# =========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            joined_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_user(user_id: int, first_name: str, username: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO users (user_id, first_name, username, joined_at)
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        first_name,
        username if username else "",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_users_count() -> int:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]

    conn.close()
    return count


def get_all_user_ids():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM users")
    rows = cur.fetchall()

    conn.close()
    return [row[0] for row in rows]


# =========================
# HELPERS
# =========================
def main_keyboard():
    keyboard = [
        ["👤 Profil", "📢 Kanal"],
        ["ℹ️ Yordam", "📊 Statistika"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def admin_keyboard():
    keyboard = [
        ["📣 Broadcast", "👥 Userlar soni"],
        ["🔙 Orqaga"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def is_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False


async def check_subscription_message(update: Update):
    buttons = [
        [InlineKeyboardButton("📢 Kanalga o'tish", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")]
    ]
    markup = InlineKeyboardMarkup(buttons)

    if update.message:
        await update.message.reply_text(
            "Botdan foydalanish uchun avval kanalga obuna bo‘ling.",
            reply_markup=markup
        )
    elif update.callback_query:
        await update.callback_query.message.reply_text(
            "Botdan foydalanish uchun avval kanalga obuna bo‘ling.",
            reply_markup=markup
        )


# =========================
# COMMANDS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    add_user(user.id, user.first_name, user.username)

    subscribed = await is_subscribed(user.id, context)
    if not subscribed:
        await check_subscription_message(update)
        return

    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}!\n\n"
        "Xush kelibsiz. Bot tayyor ishlayapti ✅",
        reply_markup=main_keyboard()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Buyruqlar:\n"
        "/start - botni ishga tushirish\n"
        "/help - yordam\n"
        "/admin - admin panel\n"
        "/id - telegram id ni ko‘rish"
    )


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Sening Telegram ID'ing: {update.effective_user.id}")


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Siz admin emassiz.")
        return

    await update.message.reply_text(
        "Admin panelga xush kelibsiz.",
        reply_markup=admin_keyboard()
    )


# =========================
# CALLBACKS
# =========================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_sub":
        subscribed = await is_subscribed(query.from_user.id, context)
        if subscribed:
            await query.message.reply_text(
                "Obuna tasdiqlandi ✅\nEndi botdan foydalanishingiz mumkin.",
                reply_markup=main_keyboard()
            )
        else:
            await query.message.reply_text("Siz hali kanalga obuna bo‘lmagansiz.")


# =========================
# MESSAGE HANDLER
# =========================
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    add_user(user.id, user.first_name, user.username)

    subscribed = await is_subscribed(user.id, context)
    if not subscribed:
        await check_subscription_message(update)
        return

    # broadcast rejimi
    if context.user_data.get("broadcast_mode") and user.id == ADMIN_ID:
        user_ids = get_all_user_ids()
        sent = 0
        failed = 0

        for uid in user_ids:
            try:
                await context.bot.send_message(chat_id=uid, text=f"📢 Admin xabari:\n\n{text}")
                sent += 1
            except Exception:
                failed += 1

        context.user_data["broadcast_mode"] = False

        await update.message.reply_text(
            f"Broadcast tugadi.\n\nYuborildi: {sent}\nXatolik: {failed}",
            reply_markup=admin_keyboard()
        )
        return

    if text == "👤 Profil":
        username = f"@{user.username}" if user.username else "yo‘q"
        await update.message.reply_text(
            f"👤 Profil\n\n"
            f"Ism: {user.first_name}\n"
            f"Username: {username}\n"
            f"ID: {user.id}"
        )

    elif text == "📢 Kanal":
        await update.message.reply_text(
            f"Kanal: {CHANNEL_USERNAME}\n"
            f"Havola: https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
        )

    elif text == "ℹ️ Yordam":
        await help_command(update, context)

    elif text == "📊 Statistika":
        count = get_users_count()
        await update.message.reply_text(f"Bot foydalanuvchilari soni: {count}")

    elif text == "📣 Broadcast":
        if user.id != ADMIN_ID:
            await update.message.reply_text("Siz admin emassiz.")
            return

        context.user_data["broadcast_mode"] = True
        await update.message.reply_text(
            "Hamma foydalanuvchilarga yuboriladigan xabarni yozing.",
            reply_markup=admin_keyboard()
        )

    elif text == "👥 Userlar soni":
        if user.id != ADMIN_ID:
            await update.message.reply_text("Siz admin emassiz.")
            return

        count = get_users_count()
        await update.message.reply_text(f"Jami userlar soni: {count}")

    elif text == "🔙 Orqaga":
        await update.message.reply_text("Asosiy menyu.", reply_markup=main_keyboard())

    else:
        await update.message.reply_text("Tugmalardan foydalaning.", reply_markup=main_keyboard())


# =========================
# MAIN
# =========================
def main():
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
