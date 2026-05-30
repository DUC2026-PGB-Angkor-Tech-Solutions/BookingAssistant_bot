# 🏨 BookingAssistantBot

A professional, modular Telegram bot designed to manage resort room bookings, check real-time room availability, and streamline customer reservations using Python and PostgreSQL. Developed by **Angkor-Tech-Solutions (Group 8)**.
**Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/BookingAssistantBot.git](https://github.com/YOUR_GITHUB_USERNAME/BookingAssistantBot.git)
   cd BookingAssistantBot
---

## 🎯 Problem Solved
* **Prevents Double-Booking:** Implements strict real-time database tracking to ensure a room cannot be reserved by two users at the same time using secure transactions.
* **Eliminates Manual Inquiries:** Customers can immediately browse and see which rooms are vacant without waiting for hotel staff to respond.
* **Simplifies Administration:** Provides an isolated, secure interface where room statuses update automatically upon checkout or confirmation.

---

## ✨ Features

### 👤 Customer Features
* 🤖 **Telegram Bot Interface:** Interactive user interface utilizing standard reply keyboards and inline contextual buttons.
* 📊 **Real-time Availability:** Fetches live vacancy data directly from the PostgreSQL database engine.
* 🗂️ **Category-wise Browsing:** Allows customers to filter rooms instantly by categories (**Standard**, **Deluxe**, and **VIP**) complete with high-quality room photos.
* 🧾 **Invoice Summary & QR Payment:** Dynamically calculates total bills and outputs a real-time **QR Code Payment** layout for smooth checkouts.

### 👨‍💼 Admin / Staff Features
* 🔒 **Secure Authorization:** Restricts access to sensitive administration modules based on verified Telegram User IDs.
* 📋 **Live Guest Reports:** Allows staff to audit all room statuses (`🟢 available` or `🔴 booked`) along with the **registered names of the customers**.
* 🛠️ **System Reset:** Instantly clears current database booking transaction logs and toggles all room statuses back to `available`.

---

## 📂 Project Structure

To keep the codebase modular, clean, and scannable, our team follows a professional file organization layout (MVC Pattern):

```text
BookingAssistantBot/
│
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
│   │   └── db_connection.py  # Initializes connections to PostgreSQL
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
