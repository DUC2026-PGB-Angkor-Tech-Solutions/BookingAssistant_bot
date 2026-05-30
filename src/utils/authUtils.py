# Simple authorization helper for Admin features
ADMIN_IDS = ["5129670141"]  # អាចដាក់លេខ ID Telegram របស់ប្អូន និងមិត្តរួមក្រុមដើម្បីធ្វើជា Admin

def is_admin(telegram_id):
    return str(telegram_id) in ADMIN_IDS