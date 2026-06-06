import os
import sys
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv

# 🌟 កែសម្រួល៖ ដោះស្រាយបញ្ហា Root Path ជាន់គ្នា (src/src) នៅលើ Cloud Render
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
if os.path.basename(current_dir) == 'src':
    sys.path.append(os.path.dirname(current_dir))

# --- ១. Import Handlers ពីការបំបែក Folder នីមួយៗ ---
from handlers.startHandler import start
from handlers.menuHandler import show_room_menu
from handlers.bookingHandler import handle_room_click, process_room_booking
from handlers.adminHandler import admin_dashboard, admin_room_report, admin_reset_rooms

# --- ២. Import Model ដើម្បីទាញទិន្នន័យ ---
from models.postgres.Room import RoomModel 

load_dotenv()

# --- ៣. អ្នកគ្រប់គ្រងរាល់ការចុចប៊ុងអត្ថបទ (Text Buttons & Form Multi-steps) ---
async def handle_text_buttons(update, context):
    text = update.message.text
    user_id = update.effective_user.id # ចាប់យក ID របស់អ្នកប្រើប្រាស់ (Telegram ID)
    
    # 🔍 ពិនិត្យមើលស្ថានភាព (State/Step) របស់ User ពី Database មុននឹងរត់ចូល Logic ធម្មតា
    db_user = RoomModel.get_user_by_telegram_id(user_id)
    
    if db_user and db_user.get('current_step') and db_user['current_step'] != 'completed':
        current_step = db_user['current_step']
        
        # ជំហានទី ១៖ ទទួលយកឈ្មោះពេញ
        if current_step == 'waiting_name':
            RoomModel.update_user_name_and_step(user_id, text, 'waiting_phone')
            await update.message.reply_text("✅ បានកត់ត្រាឈ្មោះ! 📱 សូមបញ្ចូល *លេខទូរស័ព្ទ* របស់អ្នកបន្ត៖", parse_mode="Markdown")
            return
            
        # ជំហានទី ២៖ ទទួលយកលេខទូរស័ព្ទ
        elif current_step == 'waiting_phone':
            RoomModel.update_user_phone_and_step(user_id, text, 'completed')
            
            # ចុះឈ្មោះចប់ បង្ហាញ Menu ដើមជូនគាត់
            keyboard = [["🏨 Menu", "📦 My Booking"], ["✅ Checkout", "🗑️ Clear"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await update.message.reply_text("🎉 ការចុះឈ្មោះបានជោគជ័យជាស្ថាពរ! លោកអ្នកអាចប្រើប្រាស់ម៉ឺនុយខាងក្រោមដើម្បីកក់បន្ទប់បានហើយ។", reply_markup=reply_markup)
            return
            
        # ជំហានទី ៣៖ ទទួលថ្ងៃចូលស្នាក់នៅ (ពេលកំពុងកក់បន្ទប់)
        elif current_step == 'waiting_checkin':
            context.user_data['checkin_date'] = text
            RoomModel.update_user_step(user_id, 'waiting_days')
            await update.message.reply_text("🔢 សូមបញ្ចូល *عددថ្ងៃ* ដែលអ្នកចង់ស្នាក់នៅ (ឧទាហរណ៍៖ 3)៖", parse_mode="Markdown")
            return
            
        # ជំហានទី ៤៖ ទទួលចំនួនថ្ងៃ និងបញ្ចប់ការរក្សាទុកការកក់
        elif current_step == 'waiting_days':
            try:
                days = int(text)
                room_id = context.user_data.get('selected_room_id')
                checkin_date = context.user_data.get('checkin_date')
                
                if not room_id or not checkin_date:
                    await update.message.reply_text("⚠️ មានបញ្ហាទិន្នន័យការកក់! សូមចុច 🏨 Menu ដើម្បីចាប់ផ្ដើមឡើងវិញ។")
                    RoomModel.update_user_step(user_id, 'completed')
                    return
                
                # គណនាតម្លៃសរុប (ទាញតម្លៃបន្ទប់ពី DB គុណនឹងចំនួនថ្ងៃ)
                room_info = RoomModel.get_room_by_id(room_id)
                total_amount = float(room_info['price']) * days
                
                # រក្សាទុកទិន្នន័យចូល Table bookings
                RoomModel.save_booking(user_id, room_id, checkin_date, days, total_amount)
                RoomModel.update_user_step(user_id, 'completed')
                
                await update.message.reply_text("📝 ការកក់ទុកបណ្ដោះអាសន្នត្រូវបានកត់ត្រាជោគជ័យ! សូមចុចប៊ូតុង *✅ Checkout* ខាងក្រោមដើម្បីពិនិត្យវិក្កយបត្រ និងធ្វើការបង់ប្រាក់។", parse_mode="Markdown")
            except ValueError:
                await update.message.reply_text("⚠️ សូមបញ្ចូលជាលេខចំនួនថ្ងៃស្នាក់នៅឱ្យបានត្រឹមត្រូវ (ឧទាហរណ៍៖ 2)៖")
            return

    # =========================================================
    # === ផ្នែកម៉ឺនុយធម្មតាសម្រាប់អតិថិជន (Customer Features) ===
    # =========================================================
    if text == "🏨 Menu":
        await show_room_menu(update, context)
        
    elif text == "📦 My Booking":
        bookings = RoomModel.get_user_bookings(user_id)
        if not bookings:
            await update.message.reply_text("📦 អ្នកមិនទាន់មានការកក់បន្ទប់ណាមួយនៅឡើយទេ។")
        else:
            response = "📋 បញ្ជីបន្ទប់ដែលអ្នកបានកក់ទុក៖\n"
            response += "----------------------------------\n"
            for b in bookings:
                response += f"🔹 បន្ទប់លេខ: {b[0]} | ប្រភេទ: {b[1]} | ថ្ងៃចូលស្នាក់៖ {b[3]} ({b[4]} ថ្ងៃ) | តម្លៃ: ${b[2]}\n"
            await update.message.reply_text(response)
            
    elif text == "✅ Checkout":
        bookings = RoomModel.get_user_bookings(user_id)
        if not bookings:
            await update.message.reply_text("❌ មិនមានបន្ទប់ណាមួយត្រូវទូទាត់ប្រាក់ឡើយ។ សូមកក់បន្ទប់ជាមុនសិន។")
        else:
            total_price = sum(float(b[2]) for b in bookings)
            
            response = "🧾 វិក្កយបត្រសរុប (Invoice Summary) 🧾\n"
            response += "----------------------------------\n"
            for b in bookings:
                response += f"▪️ Room {b[0]} ({b[1]}) - {b[4]} ថ្ងៃ : ${b[2]}\n"
            response += "----------------------------------\n"
            response += f"💰 ទឹកប្រាក់សរុបត្រូវទូទាត់៖ ${total_price:.2f}\n\n"
            response += "📱 សូមស្កែន QR កូដខាងក្រោមនេះ ដើម្បីធ្វើការទូទាត់ប្រាក់។ បន្ទាប់ពីទូទាត់រួច សូមចុចប៊ូតុងពិនិត្យស្ថានភាពខាងក្រោម៖"

            qr_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "qr_payment.png")

            # បង្កើតប៊ូតុង Inline ឱ្យ User ចុចផ្ទៀងផ្ទាត់ការបង់ប្រាក់
            keyboard = [[InlineKeyboardButton("🔄 ខ្ញុំបានបង់ប្រាក់រួចរាល់ (ពិនិត្យស្ថានភាព)", callback_data="verify_payment_status")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if os.path.exists(qr_image_path):
                with open(qr_image_path, 'rb') as photo:
                    await update.message.reply_photo(photo=photo, caption=response, reply_markup=reply_markup)
            else:
                await update.message.reply_text(response + "\n\n⚠️ (រកមិនឃើញហ្វាយរូបភាព QR កូដឡើយ)", reply_markup=reply_markup)
            
    elif text == "🗑️ Clear":
        is_cleared = RoomModel.clear_user_bookings(user_id)
        if is_cleared:
            await update.message.reply_text("🗑️ បានបោះបង់ និងសម្អាតទិន្នន័យការកក់របស់អ្នករួចរាល់។ បន្ទប់ត្រូវបានដាក់ឱ្យទំនេរឡើងវិញ។")
        else:
            await update.message.reply_text("❌ អ្នកមិនទាន់មានការកក់បន្ទប់ណាដែលត្រូវលុបឡើយ។")
            
    # === ផ្នែកសម្រាប់បុគ្គលិក (Admin / Staff Features) ===
    elif text == "📊 មើលរបាយការណ៍បន្ទប់":
        await admin_room_report(update, context)
        
    elif text == "🛠️ បើកបន្ទប់ទំនេរឡើងវិញ":
        await admin_reset_rooms(update, context)
        
    elif text == "🚪 ចាកចេញពី Admin Mode":
        await start(update, context)
        
    else:
        await process_room_booking(update, context)

# --- ៤. បង្កើត Web Server ក្លែងក្លាយដើម្បីដោះស្រាយលក្ខខណ្ឌ Render Free Tier ---
class HealthCheckServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is running 24/7 successfully!")

def run_health_server(port):
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckServer)
        print(f"🌍 Internal Health Check Server is listening on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ Warning: Health check server failed to bind on port {port}: {e}")

# --- ៥. ចំណុចចាប់ផ្ដើមរត់កម្មវិធី (Main Entry Point) ---
if __name__ == '__main__':
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    PORT = int(os.getenv("PORT", 10000))
    
    if not BOT_TOKEN:
        print("❌ Error: Missing TELEGRAM_BOT_TOKEN in .env file!")
        sys.exit(1)
        
    server_thread = threading.Thread(target=run_health_server, args=(PORT,), daemon=True)
    server_thread.start()
        
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # =========================================================================
    # 🗄️ យន្តការ AUTO-MIGRATION៖ បង្ខំឱ្យបង្កើត Column ស្វ័យប្រវត្ត ការពារ Error UndefinedColumn
    # =========================================================================
    from database.db_connection import get_db_connection
    db = get_db_connection()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS current_step VARCHAR(50) DEFAULT 'completed';")
            cursor.execute("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS checkin_date VARCHAR(50);")
            cursor.execute("ALTER TABLE bookings ADD COLUMN IF NOT EXISTS total_days INT DEFAULT 1;")
            cursor.execute("ALTER TABLE rooms ADD COLUMN IF NOT EXISTS room_image_url TEXT;")
            db.commit()
            cursor.close()
            db.close()
            print("🗄️ Cloud Database Auto-Migration: All required columns are verified/created successfully!")
        except Exception as db_err:
            print(f"⚠️ Database Migration Note: {db_err}")
    # =========================================================================
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_dashboard))
    
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_buttons))
    app.add_handler(CallbackQueryHandler(handle_room_click))
    
    print("🚀 BookingAssistantBot is running with Multi-step Registration...")
    app.run_polling()