from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def show_room_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Standard Room", callback_data='room_standard')],
        [InlineKeyboardButton("Deluxe Room", callback_data='room_deluxe')],
        [InlineKeyboardButton("VIP Room", callback_data='room_vip')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "📋 សូមជ្រើសរើសប្រភេទបន្ទប់ដែលអ្នកចង់កក់៖", 
        reply_markup=reply_markup
    )