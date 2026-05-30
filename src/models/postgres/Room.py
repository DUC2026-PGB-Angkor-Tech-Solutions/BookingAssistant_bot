from database.db_connection import get_db_connection

class RoomModel:
    @staticmethod
    def get_available_rooms(room_type):
        db = get_db_connection()
        if not db: return None
        cursor = db.cursor()
        cursor.execute(
            "SELECT room_number, price FROM rooms WHERE room_type = %s AND status = 'available'",
            (room_type,)
        )
        rooms = cursor.fetchall()
        cursor.close()
        db.close()
        return rooms

    # --- 🟢 មុខងារកក់បន្ទប់ថ្មី (រត់ចូល Tables ទាំង ៣ ព្រមគ្នា) ---
    @staticmethod
    def book_room(room_number, telegram_id, full_name):
        db = get_db_connection()
        if not db: return False
        try:
            cursor = db.cursor()
            
            # ១. បញ្ចូលព័ត៌មានភ្ញៀវទៅក្នុង Table users (បើមិនទាន់មាន)
            cursor.execute(
                "INSERT INTO users (telegram_id, full_name) VALUES (%s, %s) ON CONFLICT (telegram_id) DO UPDATE SET full_name = %s RETURNING user_id",
                (str(telegram_id), full_name, full_name)
            )
            user_id = cursor.fetchone()[0]
            
            # ២. ទាញយក room_id និង price ពី Table rooms
            cursor.execute("SELECT room_id, price FROM rooms WHERE room_number = %s AND status = 'available'", (room_number,))
            room_data = cursor.fetchone()
            
            if not room_data:
                return False # បើគ្មានបន្ទប់ ឬបន្ទប់មិនទំនេរ
                
            room_id, price = room_data
            
            # ៣. បង្កើតប្រវត្តិការកក់ក្នុង Table bookings
            cursor.execute(
                "INSERT INTO bookings (user_id, room_id, total_amount) VALUES (%s, %s, %s)",
                (user_id, room_id, price)
            )
            
            # ៤. ប្តូរ status ក្នុង Table rooms ទៅជា booked
            cursor.execute("UPDATE rooms SET status = 'booked' WHERE room_id = %s", (room_id,))
            
            db.commit()
            cursor.close()
            db.close()
            return True
        except Exception as e:
            print(f"❌ Booking Transaction Error: {e}")
            db.rollback() # បើមានជំហានណាមួយ Error វានឹងរុញទិន្នន័យថយក្រោយវិញ ការពារកូដបុកគ្នា
            return False

    # --- 🔵 មុខងារទី ១៖ ទាញយកបញ្ជីបន្ទប់ដែល User ម្នាក់ហ្នឹងបានកក់ (My Booking) ---
    @staticmethod
    def get_user_bookings(telegram_id):
        db = get_db_connection()
        if not db: return None
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT r.room_number, r.room_type, r.price 
            FROM bookings b
            JOIN users u ON b.user_id = u.user_id
            JOIN rooms r ON b.room_id = r.room_id
            WHERE u.telegram_id = %s AND r.status = 'booked'
            """,
            (str(telegram_id),)
        )
        bookings = cursor.fetchall()
        cursor.close()
        db.close()
        return bookings

    # --- 🔴 មុខងារទី ២៖ លុបការកក់ទាំងអស់របស់ User ម្នាក់ហ្នឹងចោល (Clear) ---
    @staticmethod
    def clear_user_bookings(telegram_id):
        db = get_db_connection()
        if not db: return False
        try:
            cursor = db.cursor()
            # កែប្រែ status បន្ទប់ឱ្យទៅជា available វិញ ផ្អែកលើការកក់របស់ភ្ញៀវម្នាក់ហ្នឹង
            cursor.execute(
                """
                UPDATE rooms SET status = 'available' WHERE room_id IN (
                    SELECT b.room_id FROM bookings b 
                    JOIN users u ON b.user_id = u.user_id 
                    WHERE u.telegram_id = %s
                )
                """,
                (str(telegram_id),)
            )
            # លុបប្រវត្តិចេញពី Table bookings
            cursor.execute(
                "DELETE FROM bookings WHERE user_id = (SELECT user_id FROM users WHERE telegram_id = %s)",
                (str(telegram_id),)
            )
            db.commit()
            cursor.close()
            db.close()
            return True
        except Exception as e:
            print(f"❌ Clear Error: {e}")
            db.rollback()
            return False