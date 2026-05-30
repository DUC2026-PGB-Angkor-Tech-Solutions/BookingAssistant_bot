from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.authUtils import is_admin
from database.db_connection import get_db_connection

# --- ១. បង្ហាញ Menu សម្រាប់តែ Admin ---
async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    
    # ផ្ទៀងផ្ទាត់សិទ្ធិ បើមិនមែន Admin មិនឱ្យចូលឡើយ
    if not is_admin(telegram_id):
        await update.message.reply_text("❌ សុំទោស! អ្នកមិនមានសិទ្ធិចូលប្រើប្រាស់មុខងារ Admin ឡើយ។")
        return

    admin_keyboard = [
        ["📊 មើលរបាយការណ៍បន្ទប់", "🛠️ បើកបន្ទប់ទំនេរឡើងវិញ"],
        ["🚪 ចាកចេញពី Admin Mode"]
    ]
    reply_markup = ReplyKeyboardMarkup(admin_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👨‍💼 ស្វាគមន៍មកកាន់ប្រព័ន្ធគ្រប់គ្រង Admin Dashboard!\nសូមជ្រើសរើសមុខងារខាងក្រោម៖", 
        reply_markup=reply_markup
    )

# --- ២. មុខងារ Admin មើលស្ថានភាពបន្ទប់ទាំងអស់ និងឈ្មោះអ្នកកក់ (កែសម្រួលថ្មី) ---
async def admin_room_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id): return

    db = get_db_connection()
    if not db: return
    
    try:
        cursor = db.cursor()
        # 🟢 ប្រើ LEFT JOIN ដើម្បីទាញយកឈ្មោះ full_name របស់ភ្ញៀវដែលបានកក់
        cursor.execute("""
            SELECT r.room_number, r.room_type, r.status, u.full_name 
            FROM rooms r
            LEFT JOIN bookings b ON r.room_id = b.room_id
            LEFT JOIN users u ON b.user_id = u.user_id
            ORDER BY r.room_number ASC
        """)
        all_rooms = cursor.fetchall()
        cursor.close()
        db.close()

        response = "📊 **របាយការណ៍ស្ថានភាពបន្ទប់បច្ចុប្បន្ន៖**\n"
        response += "----------------------------------------\n"
        
        for r in all_rooms:
            room_number, room_type, status, customer_name = r
            
            if status == 'booked':
                status_emoji = "🔴"
                # បើមានឈ្មោះក្នុង Database ឱ្យបង្ហាញឈ្មោះ បើអត់ទេដាក់ថា មិនស្គាល់ឈ្មោះ
                guest_info = f" (កក់ដោយ: {customer_name})" if customer_name else " (មិនស្គាល់ឈ្មោះ)"
            else:
                status_emoji = "🟢"
                guest_info = "" # បើបន្ទប់នៅទំនេរ available មិនបាច់បង្ហាញឈ្មោះទេ
                
            response += f"{status_emoji} បន្ទប់ {room_number} ({room_type}) -> ស្ថានភាព: {status}{guest_info}\n"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        print(f"❌ Admin Report Error: {e}")
        await update.message.reply_text("❌ 有បញ្ហាបច្ចេកទេសក្នុងការទាញយករបាយការណ៍។")

# --- ៣. មុខងារ Admin សម្អាតបន្ទប់ទាំងអស់ឱ្យទំនេរឡើងវិញ (Reset System) ---
async def admin_reset_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id): return

    db = get_db_connection()
    if not db: return

    try:
        cursor = db.cursor()
        # លុបប្រវត្តិការកក់ និងបើកបន្ទប់ឱ្យទំនេរទាំងអស់
        cursor.execute("DELETE FROM bookings")
        cursor.execute("UPDATE rooms SET status = 'available'")
        db.commit()
        cursor.close()
        db.close()
        await update.message.reply_text("🔄 ជោគជ័យ! ប្រព័ន្ធត្រូវបាន Reset។ បន្ទប់ទាំងអស់ត្រូវបានដាក់ឱ្យទំនេរ (available) ឡើងវិញហើយ។")
    except Exception as e:
        print(f"❌ Admin Reset Error: {e}")
        await update.message.reply_text("❌ មានបញ្ហាបច្ចេកទេសក្នុងការ Reset ប្រព័ន្ធ។")