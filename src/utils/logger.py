import datetime

def log_error(module_name, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [ERROR] [{module_name}]: {message}\n"
    print(log_message.strip())  # បង្ហាញលើ Terminal
    
    # កត់ចូលហ្វាយ text
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(log_message)