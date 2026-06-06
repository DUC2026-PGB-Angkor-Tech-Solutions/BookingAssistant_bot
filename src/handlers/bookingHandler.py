import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.postgres.Room import RoomModel

# --- ១. មុខងារបង្ហាញបន្ទប់ព្រមទាំងរូបភាពទៅតាមប្រភេទបន្ទប់នីមួយៗ (កែសម្រួលថ្មី) ---
async def handle_room_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = update.effective_user.id
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    
    # =========================================================================
    # 🔄 លក្ខខណ្ឌបន្ថែម៖ ស្ទាក់ចាប់ប៊ូតុង Inline ពិនិត្យស្ថានភាពបង់ប្រាក់ (Payment Verification)
    # =========================================================================
    if data == "verify_payment_status":
        await query.answer()
        # ទៅទាញមើលទិន្នន័យការកក់ចុងក្រោយបង្អស់របស់ User ម្នាក់នេះ
        latest_booking = RoomModel.get_latest_user_booking(user_id)
        
        if latest_booking and latest_booking.get('payment_status') == 'paid':
            # ករណី៖ បង់ប្រាក់ជោគជ័យ
            success_text = (
                f"{query.message.caption}\n\n"
                f"🟢 **ការបង់ប្រាក់របស់អ្នកទទួលបានជោគជ័យ!**\n"
                f"🛏️ បន្ទប់ត្រូវបានរក្សាទុកជូនលោកអ្នកជាផ្លូវការ។ សូមស្វាគមន៍មកកាន់សណ្ឋាគារយើងខ្ញុំ!"
            )
            try:
                await query.edit_message_caption(caption=success_text, parse_mode="Markdown")
            except Exception:
                await query.message.reply_text("🟢 **ការបង់ប្រាក់របស់អ្នកទទួលបានជោគជ័យ! សូមអرគុណ!**", parse_mode="Markdown")
        else:
            # ករណី៖ មិនទាន់បង់ប្រាក់ ឬមិនទាន់ទទួលបានប្រាក់
            await query.message.reply_text(
                "🔴 **ការបង់ប្រាក់មិនទទួលបានជោគជ័យទេ!**\n"
                "⚠️ ប្រព័ន្ធមិនទាន់ទទួលបានទិន្នន័យទូទាត់ប្រាក់របស់អ្នកឡើយ។ សូមពិនិត្យមើលការផ្ទេរប្រាក់ ឬព្យាយាមម្តងទៀត។", 
                parse_mode="Markdown"
            )
        return

    # =========================================================================
    # 🏨 ផ្នែកបង្ហាញបញ្ជីបន្ទប់ទំនេរតាមប្រភេទ (Standard, Deluxe, VIP)
    # =========================================================================
    await query.answer()
    
    room_configs = {
        'room_standard': {'name': 'Standard', 'image': 'standard.jpg'},
        'room_deluxe': {'name': 'Deluxe', 'image': 'deluxe.jpg'},
        'room_vip': {'name': 'VIP', 'image': 'vip.jpg'}
    }
    
    config = room_configs.get(data)

    if config:
        selected_type = config['name']
        image_name = config['image']
        
        # ទាញទិន្នន័យបន្ទប់ទំនេរពី Database
        rooms = RoomModel.get_available_rooms(selected_type)
        
        if rooms is None:
            await query.edit_message_text("❌ 有បញ្ហាបច្ចេកទេសក្នុងការភ្ជាប់ Database។")
            return
            
        if not rooms:
            await query.edit_message_text(text=f"😔 សុំទោស! បន្ទប់ប្រភេទ {selected_type} មិនមានទំនេរទេ។")
        else:
            # រៀបចំអត្ថបទបញ្ជីបន្ទប់ទំនេរ
            response = f"🏨 បញ្ជីបន្ទប់ [{selected_type}] ដែលទំនេរ៖\n"
            response += "----------------------------------\n"
            for r in rooms:
                response += f"🔹 លេខបន្ទប់: {r[0]} | តម្លៃ: ${r[1]}/យប់\n"
            response += "\n👉 សូមវាយលេខបន្ទប់ដើម្បីធ្វើការកក់ (ឧទហរណ៍: 101)"
            
            # កំណត់ផ្លូវទៅរកហ្វាយរូបភាពក្នុង Folder assets
            image_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "assets", 
                image_name
            )
            
            # លុបសារប៊ូតុងចាស់ចេញ ដើម្បីកុំឱ្យចង្អៀតប្រអប់ Chat
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception as e:
                print(f"⚠️ Cannot delete message: {e}")
            
            # ពិនិត្យមើលហ្វាយរូបភាព រួចផ្ញើចេញ
            if os.path.exists(image_path):
                with open(image_path, 'rb') as photo:
                    await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=response)
            else:
                await context.bot.send_message(chat_id=chat_id, text=response + f"\n\n⚠️ (រកមិនឃើញហ្វាយរូបភាព {image_name} នៅក្នុង assets/ ឡើយ)")

# --- ២. មុខងារចាប់យកលេខបន្ទប់ រួចសួរព័ត៌មានកក់បន្ថែមជាជំហានៗ (កែសម្រួលថ្មី) ---
async def process_room_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    user_id = update.effective_user.id
    
    # 🔍 ឆែកមើលជាមុនសិនថា តើលេខបន្ទប់ដែលគាត់វាយមក មានក្នុង Database និងទំនេរពិតមែនឬអត់
    room_info = RoomModel.get_room_by_number_if_available(user_input)
    
    if room_info:
        # 💡 បើបន្ទប់ពិតជាទំនេរមែន៖ កត់ត្រា ID បន្ទប់ទុកក្នុង memory មួយភ្លែត
        context.user_data['selected_room_id'] = room_info['room_id']
        context.user_data['booking_room_number'] = user_input
        
        # 🔄 ប្តូរស្ថានភាព User ក្នុង DB ឱ្យទៅជាវគ្គបំពេញថ្ងៃខែចូលស្នាក់នៅ
        RoomModel.update_user_step(user_id, 'waiting_checkin')
        
        await update.message.reply_text(
            f"🎯 លោកអ្នកបានជ្រើសរើសបន្ទប់លេខ [{user_input}] ល្អណាស់!\n"
            f"📅 សូមមេត្តាបញ្ចូល **ថ្ងៃដែលអ្នកត្រូវចូលមកស្នាក់នៅ** (ឧទាហរណ៍៖ 15-June-2026)៖",
            parse_mode="Markdown"
        )
    else:
        # បើវាយលេខបន្ទប់ខុស ឬបន្ទប់គេកក់បាត់ហើយ
        await update.message.reply_text(
            f"❌ មិនអាចកក់បន្ទប់លេខ {user_input} បានទេ។\n"
            f"សូមពិនិត្យមើលលេខបន្ទប់ទំនេរក្នុង 🏨 Menu ឡើងវិញ ឬបន្ទប់នេះត្រូវបានគេកក់រួចហើយ។"
        )