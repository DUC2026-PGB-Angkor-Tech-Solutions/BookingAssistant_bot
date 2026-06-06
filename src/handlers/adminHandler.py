import os
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

# --- ២. មុខងារ Admin មើលស្ថានភាពបន្ទប់ រូបភាព និងព័ត៌មានអ្នកកក់លម្អិត (កែសម្រួលថ្មី) ---
async def admin_room_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id): return

    db = get_db_connection()
    if not db: 
        await update.message.reply_text("❌ មិនអាចភ្ជាប់ទៅកាន់ Database បានទេ។")
        return
    
    await update.message.reply_text("📊 **កំពុងទាញយករបាយការណ៍ និងរូបភាពបន្ទប់ទាំងអស់ពី Cloud...**", parse_mode="Markdown")
    
    try:
        cursor = db.cursor()
        # 🟢 កែសម្រួល SQL៖ ទាញយកព័ត៌មានកក់លម្អិត លេខទូរស័ព្ទ ថ្ងៃស្នាក់នៅ ចំនួនថ្ងៃ និងស្ថានភាពបង់ប្រាក់
        cursor.execute("""
            SELECT 
                r.room_number, 
                r.room_type, 
                r.status, 
                r.room_image_url,
                u.full_name, 
                u.phone_number,
                b.checkin_date,
                b.total_days,
                b.payment_status
            FROM rooms r
            LEFT JOIN bookings b ON r.room_id = b.room_id
            LEFT JOIN users u ON b.user_id = u.user_id
            ORDER BY r.room_number ASC
        """)
        all_rooms = cursor.fetchall()
        cursor.close()
        db.close()

        # រត់ Loop ផ្ញើរាយការណ៍ចេញជារូបភាពមួយបន្ទប់ៗ
        for r in all_rooms:
            room_number, room_type, status, room_image_url, customer_name, phone_number, checkin_date, total_days, payment_status = r
            
            # រៀបចំ Caption ព័ត៌មានលម្អិតសម្រាប់បន្ទប់នីមួយៗ
            report_text = f"🏨 **បន្ទប់លេខ៖ {room_number}** ({room_type})\n"
            
            if status == 'booked':
                report_text += "🔴 ស្ថានភាព៖ **បានកក់**\n"
                
                # បង្ហាញស្ថានភាពទូទាត់ប្រាក់ជាក់ស្តែង
                if payment_status == 'paid':
                    report_text += "💰 ការទូទាត់៖ 🟢 **បានទូទាត់ប្រាក់រួចរាល់**\n"
                else:
                    report_text += "💰 ការទូទាត់៖ 🟡 **មិនទាន់ទូទាត់ប្រាក់ទេ**\n"
                    
                # បន្ថែមព័ត៌មាន Chat កក់របស់ភ្ញៀវ
                report_text += f"👤 អ្នកកក់៖ {customer_name or 'មិនស្គាល់ឈ្មោះ'}\n"
                report_text += f"📱 លេខទូរស័ព្ទ៖ {phone_number or 'មិនទាន់បំពេញ'}\n"
                report_text += f"📅 ថ្ងៃចូលស្នាក់នៅ៖ {checkin_date or 'មិនទាន់កំណត់'}\n"
                report_text += f"⏳ រយៈពេលស្នាក់នៅ៖ {total_days or 1} ថ្ងៃ\n"
            else:
                report_text += "🟢 ស្ថានភាព៖ **ទំនេរ (Available)**\n"
                report_text += "ℹ️ មិនទាន់មានការ Chat មកកក់ឡើយ។\n"
                
            report_text += "----------------------------------------"

            # 🖼️ បើមាន Link រូបភាពក្នុង Table ឱ្យផ្ញើជារូបភាព បើអត់ទេផ្ញើជាអត្ថបទធម្មតា
            if room_image_url and (room_image_url.startswith('http://') or room_image_url.startswith('https://')):
                try:
                    await update.message.reply_photo(photo=room_image_url, caption=report_text, parse_mode="Markdown")
                except Exception as img_err:
                    print(f"⚠️ Cannot send external image URL: {img_err}")
                    await update.message.reply_text(report_text, parse_mode="Markdown")
            else:
                # ករណីរកមិនឃើញ Link លើ Cloud គឺទៅរកហ្វាយរូបភាពមូលដ្ឋានក្នុង assets កុំព្យូទ័រ
                local_image_name = f"{room_type.lower()}.jpg"
                image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", local_image_name)
                
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as photo:
                        await update.message.reply_photo(photo=photo, caption=report_text, parse_mode="Markdown")
                else:
                    await update.message.reply_text(report_text, parse_mode="Markdown")
                    
    except Exception as e:
        print(f"❌ Admin Report Error: {e}")
        await update.message.reply_text("❌ មានបញ្ហាបច្ចេកទេសក្នុងការទាញយករបាយការណ៍បន្ទប់។")

# --- ៣. មុខងារ Admin សម្អាតបន្ទប់ទាំងអស់ឱ្យទំនេរឡើងវិញ (Reset System) ---
async def admin_reset_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    if not is_admin(telegram_id): return

    db = get_db_connection()
    if not db: 
        await update.message.reply_text("❌ មិនអាចភ្ជាប់ទៅកាន់ Database បានទេ។")
        return

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