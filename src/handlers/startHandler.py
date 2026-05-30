from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🏨 Menu", "📦 My Booking"],
        ["✅ Checkout", "🗑️ Clear"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "សូមស្វាគមន៍មកកាន់ Resort! សូមជ្រើសរើសមុខងារខាងក្រោម៖", 
        reply_markup=reply_markup
    )