import os
import sqlite3
from datetime import datetime, timedelta
import random
from config import Config

def get_db_connection():
    """Establish and return a SQLite database connection with row factory configured."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(seed_if_empty=True):
    """Initialize database tables and seed initial defaults."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Categories Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL,
                icon TEXT NOT NULL
            )
        """)

        # 2. Expenses Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                payment_method TEXT NOT NULL,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 3. Monthly Budgets Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(month, year)
            )
        """)

        # Seed categories if missing
        cursor.execute("SELECT COUNT(*) as count FROM categories")
        if cursor.fetchone()["count"] == 0:
            for cat in Config.DEFAULT_CATEGORIES:
                cursor.execute(
                    "INSERT INTO categories (name, color, icon) VALUES (?, ?, ?)",
                    (cat["name"], cat["color"], cat["icon"])
                )

        conn.commit()

        # Check if expenses exist; if not, seed realistic sample data
        if seed_if_empty:
            cursor.execute("SELECT COUNT(*) as count FROM expenses")
            if cursor.fetchone()["count"] == 0:
                seed_sample_data(conn)

def seed_sample_data(conn=None):
    """Seed realistic expense records across the past 45 days for demo & analytics."""
    close_conn = False
    if conn is None:
        conn = get_db_connection()
        close_conn = True

    cursor = conn.cursor()

    sample_items = [
        ("Grocery Mart Weekly Run", 68.50, "Groceries", "Debit Card", "Weekly pantry restock"),
        ("Starbucks Morning Latte", 5.75, "Food & Dining", "UPI", "Coffee with colleague"),
        ("Gasoline Fill-Up", 45.00, "Transportation", "Credit Card", "Full tank refill"),
        ("Netflix Monthly Subscription", 15.99, "Entertainment", "Credit Card", "Standard subscription"),
        ("Dinner at Olive Garden", 52.40, "Food & Dining", "Credit Card", "Family weekend dinner"),
        ("Electric & Power Bill", 84.20, "Utilities & Bills", "Net Banking", "Monthly power consumption"),
        ("Running Shoes - Nike", 110.00, "Shopping", "Credit Card", "Gym workout shoes"),
        ("Pharmacy Medicines", 24.30, "Health & Fitness", "Cash", "Vitamins and cold medicine"),
        ("Uber Ride to Downtown", 18.50, "Transportation", "UPI", "Ride to client meeting"),
        ("Spotify Premium", 9.99, "Entertainment", "UPI", "Music subscription"),
        ("Supermarket Organic Produce", 42.10, "Groceries", "Debit Card", "Vegetables & fruits"),
        ("Udemy Python Course", 14.99, "Education", "Credit Card", "Course on Web Architecture"),
        ("High Speed Home Wi-Fi", 60.00, "Utilities & Bills", "Net Banking", "Broadband bill"),
        ("Weekend Cinema Tickets & Popcorn", 32.00, "Entertainment", "Debit Card", "Movie night"),
        ("Gym Membership Monthly", 40.00, "Health & Fitness", "Credit Card", "Monthly gym dues"),
        ("Quick Lunch Sandwich", 9.50, "Food & Dining", "UPI", "Lunch break snack"),
        ("Amazon Essentials Order", 38.75, "Shopping", "Credit Card", "Home organizers"),
        ("Train Commute Monthly Pass", 65.00, "Transportation", "Debit Card", "Metro pass"),
        ("Dental Cleaning Checkup", 85.00, "Health & Fitness", "Credit Card", "Routine dental visit"),
        ("Weekend Coffee & Pastry", 8.25, "Food & Dining", "Cash", "Cafe morning"),
        ("Books from Barnes & Noble", 34.00, "Education", "Debit Card", "System Design book"),
        ("Water Utility Bill", 28.50, "Utilities & Bills", "Net Banking", "Water municipal bill"),
        ("New Wireless Mouse", 29.99, "Shopping", "UPI", "Ergonomic computer mouse"),
        ("Flight Ticket to Visit Family", 210.00, "Travel", "Credit Card", "Roundtrip flight booking"),
        ("Hotel Stay Deposit", 125.00, "Travel", "Credit Card", "Weekend getaway booking"),
        ("Car Wash & Detailing", 20.00, "Transportation", "Cash", "Exterior clean & vacuum"),
        ("Dinner Takeout Thai Curry", 26.50, "Food & Dining", "UPI", "Dinner with friends"),
        ("Hardware Store Supplies", 17.80, "Miscellaneous", "Cash", "Lightbulbs and screwdrivers"),
    ]

    today = datetime.now()

    # Clear existing expenses if seeding on demand
    cursor.execute("DELETE FROM expenses")

    for i, (title, base_amount, category, payment_method, notes) in enumerate(sample_items):
        # Distribute dates evenly over last 40 days
        days_ago = (i * 40) // len(sample_items)
        expense_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Add slight variation to amounts
        amount = round(base_amount * random.uniform(0.92, 1.08), 2)

        cursor.execute("""
            INSERT INTO expenses (title, amount, category, date, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, amount, category, expense_date, payment_method, notes))

    # Set default monthly budget for current month & year
    current_month = today.month
    current_year = today.year
    cursor.execute("""
        INSERT OR REPLACE INTO budgets (month, year, amount)
        VALUES (?, ?, ?)
    """, (current_month, current_year, 1500.00))

    conn.commit()
    if close_conn:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized and sample data seeded successfully.")
