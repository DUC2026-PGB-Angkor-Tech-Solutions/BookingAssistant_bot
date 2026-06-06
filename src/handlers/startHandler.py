from models.postgres.Room import RoomModel
from telegram import ReplyKeyboardMarkup

async def start(update, context):
    user = update.effective_user
    telegram_id = str(user.id)
    full_name = user.full_name
    
    # ពិនិត្យមើលថាតើមាន User នេះក្នុង Database ឬនៅ
    # ឧបមាថា RoomModel.get_or_create_user ត្រលប់មកវិញនូវព័ត៌មាន User
    db_user = RoomModel.get_user_by_telegram_id(telegram_id)
    
    if not db_user:
        # បើមិនទាន់មានគណនី ឱ្យគាត់ចាប់ផ្ដើមបំពេញឈ្មោះ
        RoomModel.create_user(telegram_id, full_name, step='waiting_name')
        await update.message.reply_text("👋 សូមស្វាគមន៍មកកាន់ប្រព័ន្ធកក់បន្ទប់! ដើម្បីបន្ត សូមមេត្តាបញ្ចូល *ឈ្មោះពេញ* របស់អ្នក៖", parse_mode="Markdown")
    elif db_user['phone_number'] is None:
        RoomModel.update_user_step(telegram_id, 'waiting_phone')
        await update.message.reply_text("📱 សូមបញ្ចូល *លេខទូរស័ព្ទ* របស់អ្នកដើម្បីបន្ត៖", parse_mode="Markdown")
    else:
        # បើមានព័ត៌មានគ្រប់ហើយ បង្ហាញ Menu ធម្មតា
        keyboard = [["🏨 Menu", "📦 My Booking"], ["✅ Checkout", "🗑️ Clear"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(f"🏨 ជំរាបសួរ {db_user['full_name']}! សូមជ្រើសរើសសេវាកម្មខាងក្រោម៖", reply_markup=reply_markup)