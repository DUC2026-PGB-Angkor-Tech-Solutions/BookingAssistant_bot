from database.db_connection import get_db_connection

class BookingModel:
    @staticmethod
    def update_payment_status(booking_id, status='paid'):
        db = get_db_connection()
        if not db: return False
        cursor = db.cursor()
        cursor.execute(
            "UPDATE bookings SET payment_status = %s WHERE booking_id = %s",
            (status, booking_id)
        )
        db.commit()
        cursor.close()
        db.close()
        return True