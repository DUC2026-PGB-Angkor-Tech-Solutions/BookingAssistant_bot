import os
import sys
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from dotenv import load_dotenv

# បន្ថែមរុក្ខវិថី (Path) ដើម្បីឱ្យ Python ស្គាល់ Folder ទាំងអស់នៅក្នុង src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- ១. Import Handlers ពីការបំបែក Folder នីមួយៗ ---
from handlers.startHandler import start
from handlers.menuHandler import show_room_menu
from handlers.bookingHandler import handle_room_click, process_room_booking
from handlers.adminHandler import admin_dashboard, admin_room_report, admin_reset_rooms

# --- ២. Import Model ដើម្បីទាញទិន្នន័យ ---
from models.postgres.Room import RoomModel 

load_dotenv()

# --- ៣. អ្នកគ្រប់គ្រងរាល់ការចុចប៊ូតុងអត្ថបទ (Text Buttons) ---
async def handle_text_buttons(update, context):
    text = update.message.text
    user_id = update.effective_user.id # ចាប់យក ID របស់អ្នកប្រើប្រាស់ (Telegram ID)
    
    # === ផ្នែកសម្រាប់អតិថិជន (Customer Features) ===
    if text == "🏨 Menu":
        await show_room_menu(update, context)
        
    elif text == "📦 My Booking":
        # 🟢 មុខងារទី ១៖ មើលប្រវត្តិការកក់
        bookings = RoomModel.get_user_bookings(user_id)
        if not bookings:
            await update.message.reply_text("📦 អ្នកមិនទាន់មានការកក់បន្ទប់ណាមួយនៅឡើយទេ។")
        else:
            response = "📋 បញ្ជីបន្ទប់ដែលអ្នកបានកក់ទុក៖\n"
            response += "----------------------------------\n"
            for b in bookings:
                response += f"🔹 បន្ទប់លេខ: {b[0]} | ប្រភេទ: {b[1]} | តម្លៃ: ${b[2]}\n"
            await update.message.reply_text(response)
            
    elif text == "✅ Checkout":
        # 🔵 មុខងារទី ២៖ គិតលុយ បង្ហាញវិក្កយបត្រសរុប និងផ្ញើផ្ទាំង QR កូដបង់ប្រាក់ពិតប្រាកដ
        bookings = RoomModel.get_user_bookings(user_id)
        if not bookings:
            await update.message.reply_text("❌ មិនមានបន្ទប់ណាមួយត្រូវទូទាត់ប្រាក់ឡើយ។ សូមកក់បន្ទប់ជាមុនសិន។")
        else:
            total_price = sum(float(b[2]) for b in bookings) # គណនាតម្លៃលុយសរុប
            
            # រៀបចំអត្ថបទវិក្កយបត្រ
            response = "🧾 វិក្កយបត្រសរុប (Invoice Summary) 🧾\n"
            response += "----------------------------------\n"
            for b in bookings:
                response += f"▪️ Room {b[0]} ({b[1]}) : ${b[2]}\n"
            response += "----------------------------------\n"
            response += f"💰 ទឹកប្រាក់សរុបត្រូវទូទាត់៖ ${total_price:.2f}\n\n"
            response += "📱 សូមស្កែន QR កូដខាងក្រោមនេះ ដើម្បីធ្វើការទូទាត់ប្រាក់ពិតប្រាកដ។"

            # 🟢 កំណត់ផ្លូវទៅកាន់ហ្វាយរូបភាព QR (គណនាចេញពីទីតាំង app.py ថយក្រោយ ១ ជំហានចូល assets)
            qr_image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "qr_payment.png")

            # ពិនិត្យមើលថាតើមានហ្វាយរូបភាពពិតមែនឬអត់ ការពារកូដដួល
            if os.path.exists(qr_image_path):
                # ផ្ញើរូបភាព QR ទៅកាន់ Telegram ព្រមទាំងភ្ជាប់អត្ថបទវិក្កយបត្រនៅពីក្រោមរូប (caption)
                with open(qr_image_path, 'rb') as photo:
                    await update.message.reply_photo(photo=photo, caption=response)
            else:
                # បើភ្លេចដាក់រូបភាព ឱ្យវាផ្ញើតែអត្ថបទសិន រួចប្រាប់ជា Warning
                await update.message.reply_text(response + "\n\n⚠️ (រកមិនឃើញហ្វាយរូបភាព QR កូដនៅក្នុង assets/qr_payment.png ឡើយ)")
            
    elif text == "🗑️ Clear":
        # 🔴 មុខងារទី ៣៖ លុបការកក់ទាំងអស់ចោលឡើងវិញ
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
        await start(update, context) # នាំត្រឡប់ទៅផ្ទាំងប៊ូតុងរបស់ភ្ញៀវវិញ
        
    else:
        # បើមិនមែនចុចប៊ូតុងខាងលើទាំងអស់ទេ គឺផ្ញើលេខបន្ទប់មកកក់
        await process_room_booking(update, context)

# --- ៤. ចំណុចចាប់ផ្ដើមរត់កម្មវិធី (Main Entry Point) ---
if __name__ == '__main__':
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not BOT_TOKEN:
        print("❌ Error: Missing TELEGRAM_BOT_TOKEN in .env file!")
        sys.exit(1)
        
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # ចុះឈ្មោះមុខងារស្ដាប់ពាក្យបញ្ជា (Commands)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_dashboard)) # 👨‍💼 ពាក្យបញ្ជាបើកផ្ទាំង Admin
    
    # ចុះឈ្មោះមុខងារស្ដាប់ប៊ូតុងអត្ថបទ និងប៊ូតុងក្នុងសារ (Inline)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text_buttons))
    app.add_handler(CallbackQueryHandler(handle_room_click))
    
    print("🚀 BookingAssistantBot is running with Customer & Admin Logics...")
    app.run_polling()