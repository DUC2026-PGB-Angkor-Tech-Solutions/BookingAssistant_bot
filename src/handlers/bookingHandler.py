import os
from telegram import Update
from telegram.ext import ContextTypes
from models.postgres.Room import RoomModel

# --- ១. មុខងារបង្ហាញបន្ទប់ព្រមទាំងរូបភាពទៅតាមប្រភេទបន្ទប់នីមួយៗ (កែសម្រួលថ្មី) ---
async def handle_room_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # ចាប់យក Chat ID និង Message ID ចាស់ ដើម្បីលុបសារ Inline Button ចាស់ចោល
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    
    # ផ្គូផ្គង Callback Data ជាមួយឈ្មោះប្រភេទបន្ទប់ និងឈ្មោះហ្វាយរូបភាព
    room_configs = {
        'room_standard': {'name': 'Standard', 'image': 'standard.jpg'},
        'room_deluxe': {'name': 'Deluxe', 'image': 'deluxe.jpg'},
        'room_vip': {'name': 'VIP', 'image': 'vip.jpg'}
    }
    
    config = room_configs.get(query.data)

    if config:
        selected_type = config['name']
        image_name = config['image']
        
        # ទាញទិន្នន័យបន្ទប់ទំនេរពី Database
        rooms = RoomModel.get_available_rooms(selected_type)
        
        if rooms is None:
            await query.edit_message_text("❌ មានបញ្ហាបច្ចេកទេសក្នុងការភ្ជាប់ Database។")
            return
            
        if not rooms:
            await query.edit_message_text(text=f"😔 សុំទោស! បន្ទប់ប្រភេទ {selected_type} មិនមានទំនេរទេ។")
        else:
            # រៀបចំអត្ថបទបញ្ជីបន្ទប់ទំនេរ
            response = f"🏨 បញ្ជីបន្ទប់ [{selected_type}] ដែលទំនេរ៖\n"
            response += "----------------------------------\n"
            for r in rooms:
                response += f"🔹 លេខបន្ទប់: {r[0]} | តម្លៃ: ${r[1]}\n"
            response += "\n👉 សូមវាយលេខបន្ទប់ដើម្បីធ្វើការកក់ (ឧទាហរណ៍: 101)"
            
            # កំណត់ផ្លូវទៅរកហ្វាយរូបភាពក្នុង Folder assets
            # (គណនាចេញពីទីតាំង src/handlers/bookingHandler.py ថយក្រោយ ២ ជំហានដើម្បីចូល assets)
            image_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                "assets", 
                image_name
            )
            
            # លុបសារប៊ូតុងចាស់ចេញ ដើម្បីកុំឱ្យចង្អៀតប្រអប់ Chat របស់ភ្ញៀវ
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception as e:
                print(f"⚠️ Cannot delete message: {e}")
            
            # ពិនិត្យមើលថាតើមានហ្វាយរូបភាពពិតមែនឬអត់
            if os.path.exists(image_path):
                # ផ្ញើរូបភាពបន្ទប់ រួចភ្ជាប់អត្ថបទបញ្ជីបន្ទប់ទំនេរនៅខាងក្រោមរូប (Caption)
                with open(image_path, 'rb') as photo:
                    await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=response)
            else:
                # បើរកមិនឃើញរូបភាព ឱ្យផ្ញើត្រឹមតែអត្ថបទធម្មតា ការពារ Bot គាំង
                await context.bot.send_message(chat_id=chat_id, text=response + f"\n\n⚠️ (រកមិនឃើញហ្វាយរូបភាព {image_name} នៅក្នុង assets/ ឡើយ)")

# --- ២. មុខងារចាប់យកលេខបន្ទប់ដែល Customer វាយផ្ញើមក (រក្សាទុកដដែល) ---
async def process_room_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    telegram_id = update.effective_user.id
    
    # ចាប់យកឈ្មោះរបស់ភ្ញៀវពី Telegram
    first_name = update.effective_user.first_name or ""
    last_name = update.effective_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip() or "Telegram User"
    
    # បញ្ជូនទៅកាន់ Model ដើម្បីកក់ទុកក្នុង 3-Tables Database
    is_success = RoomModel.book_room(user_input, telegram_id, full_name)
    
    if is_success:
        await update.message.reply_text(
            f"🎉 អបអរសាទរ! អ្នកបានកក់បន្ទប់លេខ [{user_input}] រួចរាល់ហើយ។\n"
            "សូមចុចប៊ូតុង ✅ Checkout ដើម្បីពិនិត្យមើលវិក្កយបត្រ។"
        )
    else:
        await update.message.reply_text(
            f"❌ មិនអាចកក់បន្ទប់លេខ {user_input} បានទេ។\n"
            "សូមពិនិត្យមើលលេខបន្ទប់ទំនេរឡើងវិញ ឬបន្ទប់នេះត្រូវបានគេកក់រួចហើយ។"
        )