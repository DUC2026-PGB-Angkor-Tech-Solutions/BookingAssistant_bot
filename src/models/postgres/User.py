from database.db_connection import get_db_connection

class UserModel:
    @staticmethod
    def update_phone(telegram_id, phone_number):
        db = get_db_connection()
        if not db: return False
        cursor = db.cursor()
        cursor.execute(
            "UPDATE users SET phone_number = %s WHERE telegram_id = %s",
            (phone_number, str(telegram_id))
        )
        db.commit()
        cursor.close()
        db.close()
        return True