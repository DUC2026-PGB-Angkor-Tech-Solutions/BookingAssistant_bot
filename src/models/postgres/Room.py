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

    # --- 🟢 មុខងារកក់បន្ទប់ថ្មី (រត់ចូល Tables ទាំង ៣ ព្រមគ្នា និងគាំទ្រលក្ខខណ្ឌចាស់-ថ្មី) ---
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
            db.rollback() 
            return False

    # --- 🔵 មុខងារទី ១៖ ទាញយកបញ្ជីបន្ទប់ដែល User ម្នាក់ហ្នឹងបានកក់ (My Booking) ---
    @staticmethod
    def get_user_bookings(telegram_id):
        db = get_db_connection()
        if not db: return None
        cursor = db.cursor()
        cursor.execute(
            """
            SELECT r.room_number, r.room_type, b.total_amount, b.checkin_date, b.total_days 
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

    # =========================================================================
    # 🌟 ផ្នែកបន្ថែមថ្មី៖ មុខងារគាំទ្រលក្ខខណ្ឌចុះឈ្មោះជាជំហានៗ និងរក្សាទុកការកក់លម្អិត
    # =========================================================================

    # ១. ទាញទិន្នន័យ User តាមរយៈ Telegram ID ដើម្បីឆែកមើលជំហានបំពេញទម្រង់ (Step)
    @staticmethod
    def get_user_by_telegram_id(telegram_id):
        db = get_db_connection()
        if not db: return None
        cursor = db.cursor()
        cursor.execute("SELECT user_id, telegram_id, full_name, phone_number, current_step FROM users WHERE telegram_id = %s", (str(telegram_id),))
        row = cursor.fetchone()
        cursor.close()
        db.close()
        if row:
            return {'user_id': row[0], 'telegram_id': row[1], 'full_name': row[2], 'phone_number': row[3], 'current_step': row[4]}
        return None

    # ២. បង្កើតគណនី User ថ្មីដំបូង រួចដាក់ស្ថានភាពឱ្យរង់ចាំបំពេញឈ្មោះ
    @staticmethod
    def create_user(telegram_id, full_name, step='waiting_name'):
        db = get_db_connection()
        if not db: return
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (telegram_id, full_name, current_step) VALUES (%s, %s, %s) ON CONFLICT (telegram_id) DO NOTHING",
            (str(telegram_id), full_name, step)
        )
        db.commit()
        cursor.close()
        db.close()

    # ៣. Update ឈ្មោះ និងប្តូរទៅជំហានបន្ទាប់
    @staticmethod
    def update_user_name_and_step(telegram_id, name, next_step):
        db = get_db_connection()
        if not db: return
        cursor = db.cursor()
        cursor.execute("UPDATE users SET full_name = %s, current_step = %s WHERE telegram_id = %s", (name, next_step, str(telegram_id),))
        db.commit()
        cursor.close()
        db.close()

    # ៤. Update លេខទូរស័ព្ទ និងប្តូរទៅជំហានបញ្ចប់
    @staticmethod
    def update_user_phone_and_step(telegram_id, phone, next_step):
        db = get_db_connection()
        if not db: return
        cursor = db.cursor()
        cursor.execute("UPDATE users SET phone_number = %s, current_step = %s WHERE telegram_id = %s", (phone, next_step, str(telegram_id),))
        db.commit()
        cursor.close()
        db.close()

    # ៥. Update តែស្ថានភាពជំហាន (Step) របស់ User
    @staticmethod
    def update_user_step(telegram_id, step):
        db = get_db_connection()
        if not db: return
        cursor = db.cursor()
        cursor.execute("UPDATE users SET current_step = %s WHERE telegram_id = %s", (step, str(telegram_id),))
        db.commit()
        cursor.close()
        db.close()

    # ៦. ឆែកមើលថាតើលេខបន្ទប់ដែលភ្ញៀវវាយបញ្ចូល មាននិងទំនេរពិតមែនឬអត់
    @staticmethod
    def get_room_by_number_if_available(room_number):
        db = get_db_connection()
        if not db: return None
        cursor = db.cursor()
        cursor.execute("SELECT room_id, price FROM rooms WHERE room_number = %s AND status = 'available'", (str(room_number),))
        row = cursor.fetchone()
        cursor.close()
        db.close()
        if row:
            return {'room_id': row[0], 'price': row[1]}
        return None

    # ៧. ទាញទិន្នន័យបន្ទប់តាមរយៈ ID
    @staticmethod
    def get_room_by_id(room_id):
        db = get_db_connection()
        if not db: return None
        cursor = db.cursor()
        cursor.execute("SELECT room_id, room_number, price FROM rooms WHERE room_id = %s", (room_id,))
        row = cursor.fetchone()
        cursor.close()
        db.close()
        if row:
            return {'room_id': row[0], 'room_number': row[1], 'price': row[2]}
        return None

    # ៨. រក្សាទុកទិន្នន័យកក់លម្អិតចូល Table bookings និងប្តូរ status បន្ទប់ទៅជា 'booked'
    @staticmethod
    def save_booking(telegram_id, room_id, checkin_date, total_days, total_amount):
        db = get_db_connection()
        if not db: return
        try:
            cursor = db.cursor()
            # បម្លែង telegram_id ទៅជា user_id ផ្ទាល់ក្នុង Table users
            cursor.execute("SELECT user_id FROM users WHERE telegram_id = %s", (str(telegram_id),))
            res = cursor.fetchone()
            if not res: return
            user_id = res[0]
            
            # បញ្ចូលព័ត៌មានទៅកាន់តារាង bookings រួមទាំងថ្ងៃចូល និងចំនួនថ្ងៃ
            cursor.execute(
                """INSERT INTO bookings (user_id, room_id, checkin_date, total_days, total_amount, payment_status) 
                   VALUES (%s, %s, %s, %s, %s, 'pending')""",
                (user_id, room_id, checkin_date, total_days, total_amount)
            )
            # Update ស្ថានភាពបន្ទប់ទៅជា 'booked'
            cursor.execute("UPDATE rooms SET status = 'booked' WHERE room_id = %s", (room_id,))
            db.commit()
            cursor.close()
        except Exception as e:
            print(f"❌ Save booking error: {e}")
            db.rollback()
        finally:
            db.close()

    # ៩. ទាញយកទិន្នន័យការកក់ចុងក្រោយដើម្បីពិនិត្យស្ថានភាពបង់ប្រាក់ (Payment Verification)
    @staticmethod
    def get_latest_user_booking(telegram_id):
        db = get_db_connection()
        if not db: return None
        cursor = db.cursor()
        cursor.execute(
            """SELECT b.payment_status FROM bookings b
               JOIN users u ON b.user_id = u.user_id
               WHERE u.telegram_id = %s ORDER BY b.booking_id DESC LIMIT 1""",
            (str(telegram_id),)
        )
        row = cursor.fetchone()
        cursor.close()
        db.close()
        if row:
            return {'payment_status': row[0]}
        return None