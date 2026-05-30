# 🏨 BookingAssistantBot

A professional and modular Telegram bot designed to manage resort room bookings, check real-time room availability, and streamline customer reservations using Python and PostgreSQL. Developed by **Angkor-Tech-Solutions (Group 8)**.

## 🎯 Problem Solved
* **Prevents Double-Booking:** Implements strict real-time database tracking to ensure a room cannot be reserved by two users at the same time using secure ACID transactions.
* **Eliminates Manual Inquiries:** Customers can immediately browse and see which rooms are vacant without waiting for hotel/resort staff to respond manually.
* **Simplifies Administration:** Provides a centralized dashboard interface where room statuses update automatically upon customer booking, checkout, or staff reset.

## ✨ Features
* 🤖 **Telegram Bot Interface:** Interactive user interface utilizing standard reply keyboards for navigation and inline contextual buttons for room types.
* 📊 **Real-time Availability:** Fetches live vacancy data directly from the PostgreSQL relational database engine.
* 🗂️ **Category-wise Browsing:** Allows customers to filter rooms instantly by categories: **Standard**, **Deluxe**, and **VIP** complete with dynamic property photos.
* 🧾 **Invoice Summary & QR Payment:** Dynamically calculates total bills and outputs a real-time **QR Code Payment** layout for smooth financial checkouts.
* 🔒 **Secure Data Handling:** Uses environment variables (`.env`) to isolate sensitive bot tokens and backend database administrative credentials.

---

## 🚀 Quick Start

### Prerequisites
* **Python** (v3.10 or higher)
* **PostgreSQL** database server installed and running
* A Telegram Account

### Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/DUC2026-PGB-Angkor-Tech-Solutions/BookingAssistant_bot.git](https://github.com/DUC2026-PGB-Angkor-Tech-Solutions/BookingAssistant_bot.git)
   cd BookingAssistant_bot
2.  **Install required dependencies**
  ```Bash
pip install -r requirements.txt
 ```

3. **Create a Telegram Bot**

Open Telegram and search for @BotFather

Send /newbot command and follow instructions to receive your HTTP API Token

Copy the bot token you receive


4. **Configure environment**
# Copy the template file to create your active configuration
# On Windows PowerShell:
copy .env.example .env
Open the .env file and input your actual tokens and credentials (see Configuration section below)


5.**Run the bot**
```Bash
python src/app.py
```
📖 How to Use
For Customers (Resort Guests)
Start the bot

Open Telegram, search for your bot, and send /start.

The bot will initialize and display the primary navigation keyboard buttons.

Browse Available Rooms

Click "🏨 Menu" to see room categories.

Choose from Standard Room, Deluxe Room, or VIP Room. The bot will display room details, prices, and an aesthetic photo of the room.

Book a Room

Simply reply by typing the exact room number (e.g., 103) shown in the vacant list.

The bot will process the transaction, update PostgreSQL, and confirm your booking.

Check Bookings & Payment

Click "📦 My Booking" to view your active reservations.

Click "✅ Checkout" to receive an itemized invoice summary alongside your Payment QR Code to complete the transaction.

Click "🗑️ Clear" if you wish to cancel all your active bookings.

For Managers (Resort Admins)
Access Admin Panel

Send the secret command /admin to open the secure administrative dashboard.

Note: Your Telegram ID must be whitelisted in src/utils/authUtils.py.

Live Audits & Controls

Click "📊 មើលរបាយការណ៍បន្ទប់" to fetch a live report of all rooms, displaying current statuses (🟢 available / 🔴 booked) along with the full names of the guests.

Click "🛠️ បើកបន្ទប់ទំនេរឡើងវិញ" to trigger a complete system purge, erasing active bookings and resetting all rooms back to available status.

Click "🚪 ចាកចេញពី Admin Mode" to switch back to the standard customer workspace.
💡 Usage Examples
Booking a Room

```Bash
Customer: 103
Bot: 🎉 អបអរសាទរ! អ្នកបានកក់បន្ទប់លេខ [103] រួចរាល់ហើយ។
     សូមចុចប៊ូតុង ✅ Checkout ដើម្បីពិនិត្យមើលវិក្កយបត្រ។
     ```
     Admin Live Report

```Bash
     Admin: [Clicks 📊 មើលរបាយការណ៍បន្ទប់]
Bot: 📊 របាយការណ៍ស្ថានភាពបន្ទប់បច្ចុប្បន្ន៖
     ----------------------------------------
     🟢 បន្ទប់ 101 (Standard) -> ស្ថានភាព: available
     🟢 បន្ទប់ 102 (Deluxe) -> ស្ថានភាព: available
     🔴 បន្ទប់ 103 (VIP) -> ស្ថានភាព: booked (កក់ដោយ: Kimrong)
     🏗️ Project Structure
       ```Bash
         BookingAssistantBot/
├── assets/                   # Local media storage for properties and payments
│   ├── standard.jpg          # Standard room preview image
│   ├── deluxe.jpg            # Deluxe room preview image
│   ├── vip.jpg               # VIP room preview image
│   └── qr_payment.png        # Active Bakong/KHQR payment code
│
├── src/                      # Core source code directory
│   ├── app.py                # Main application entry point & router
│   │
│   ├── database/             # Persistent storage connection modules
│   │   └── db_connection.py  # Initializes connection pool to PostgreSQL
│   │
│   ├── handlers/             # Modular interaction and controller logic
│   │   ├── startHandler.py   # Processes the initial welcome menu
│   │   ├── menuHandler.py    # Manages category-wise room displays
│   │   ├── bookingHandler.py # Handles room selections and registration
│   │   └── adminHandler.py   # Controls backend reports and system resets
│   │
│   ├── models/               # Data Layer (PostgreSQL Query bindings)
│   │   └── postgres/
│   │       ├── Room.py       # Room status updates and fetching logic
│   │       ├── User.py       # Telegram user profile caching
│   │       └── Booking.py    # Payment status records
│   │
│   └── utils/                # Helper utilities
│       ├── authUtils.py      # Admin verification middleware
│       ├── currencyUtils.py  # Standard financial formatting ($ USD)
│       └── logger.py         # Error logging automated scripts
│
├── .env                      # Local environment configurations (HIDDEN & SECURE)
├── .env.example              # Sample template configuration file for teammates
├── .gitignore                # Instructs Git to ignore sensitive files
├── requirements.txt          # Production application library packages
└── README.md                 # Primary project overview and documentation
     ```
     🔧 Configuration
Environment Variables

  ```Bash
  Variable,Description,Required
TELEGRAM_BOT_TOKEN,Your Telegram bot token generated from @BotFather,🟢 Yes
DB_HOST,Database host network location (localhost),🟢 Yes
DB_NAME,The designated target database (booking_db),🟢 Yes
DB_USER,Authorized PostgreSQL username (postgres),🟢 Yes
DB_PASSWORD,Secure credential phrase to access pgAdmin database,🟢 Yes
DB_PORT,Listening network port for PostgreSQL (5432),🟢 Yes
   ```
📊 Data Storage (PostgreSQL Relational Schema)
To maximize data durability and prevent anomalies, the data infrastructure is split into 3 normalized tables:

rooms - Stores physical asset statuses and rates.

users - Caches registered clients verified by Telegram IDs.

bookings - Bridges transactions, preserving auditing trails even if checkouts are completed.

🤝 Contributing
Fork the repository

Create your feature branch (git checkout -b feature/AmazingFeature)

Commit changes (git commit -m 'Add some AmazingFeature')

Push to branch (git push origin feature/AmazingFeature)

Open a Pull Request

📝 License
This project is licensed under the MIT License.


👥 Team Members (Group 8 - Angkor-Tech-Solutions)

Kimrong - Project Manager & Lead Backend Developer (GitHub Management & Admin Panel)

Doung Sophy - Database Administrator & SQL Engineer (Schema Architecture & SQL Operations)

Chhiam Malin - UI/UX Designer & Frontend Handler (Reply/Inline Keyboards & Assets Integration)

Sorng Visal - Core Logic & Reservation Developer (Transaction Controls & Invoicing Mathematics)

Soy Long - QA Engineer & Code Reviewer (System Testing, Logging, & Package Dependency Configuration)

Made with ❤️ by Angkor-Tech-Solutions Team - 202
