import os
import sqlite3
from datetime import datetime, timedelta
import random
from contextlib import contextmanager
from config import Config

@contextmanager
def get_db_connection():
    """Establish and yield a SQLite connection with row factory, closing it reliably."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()

def init_db(seed_demo=True):
    """Initialize database tables. Real user expenses are kept completely separate from demo preview data."""
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

        # 2. Real User Expenses Table (Starts empty and strictly stores user-added transactions)
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

        # 3. Demo Preview Expenses Table (Isolated sandbox for demo preview)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demo_expenses (
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

        # 4. Monthly Budgets Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                is_demo INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(month, year, is_demo)
            )
        """)

        # Migrate budgets table if it has the old UNIQUE(month, year) constraint
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='budgets'")
        table_sql_row = cursor.fetchone()
        if table_sql_row and "UNIQUE(month, year)" in table_sql_row["sql"] and "UNIQUE(month, year, is_demo)" not in table_sql_row["sql"]:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets_migration (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    amount REAL NOT NULL CHECK(amount > 0),
                    is_demo INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(month, year, is_demo)
                )
            """)
            cursor.execute("""
                INSERT OR IGNORE INTO budgets_migration (id, month, year, amount, is_demo, created_at)
                SELECT id, month, year, amount, 1, created_at FROM budgets
            """)
            cursor.execute("DROP TABLE budgets")
            cursor.execute("ALTER TABLE budgets_migration RENAME TO budgets")

        # Check if is_demo column exists in budgets, add if missing
        cursor.execute("PRAGMA table_info(budgets)")
        budget_cols = [col["name"] for col in cursor.fetchall()]
        if "is_demo" not in budget_cols:
            cursor.execute("ALTER TABLE budgets ADD COLUMN is_demo INTEGER DEFAULT 0")

        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_budgets_month_year_demo ON budgets(month, year, is_demo)")

        # Seed categories if missing
        cursor.execute("SELECT COUNT(*) as count FROM categories")
        if cursor.fetchone()["count"] == 0:
            for cat in Config.DEFAULT_CATEGORIES:
                cursor.execute(
                    "INSERT INTO categories (name, color, icon) VALUES (?, ?, ?)",
                    (cat["name"], cat["color"], cat["icon"])
                )

        conn.commit()

        # Populate demo_expenses sandbox if empty
        if seed_demo:
            cursor.execute("SELECT COUNT(*) as count FROM demo_expenses")
            if cursor.fetchone()["count"] == 0:
                seed_sample_data(conn)

def seed_sample_data(conn=None):
    """Seed sample records strictly into the demo_expenses preview table."""
    if conn is None:
        with get_db_connection() as new_conn:
            seed_sample_data(new_conn)
        return

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

    # Clear demo sandbox table only
    cursor.execute("DELETE FROM demo_expenses")

    for i, (title, base_amount, category, payment_method, notes) in enumerate(sample_items):
        days_ago = (i * 40) // len(sample_items)
        expense_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        amount = round(base_amount * random.uniform(0.94, 1.06), 2)

        cursor.execute("""
            INSERT INTO demo_expenses (title, amount, category, date, payment_method, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, amount, category, expense_date, payment_method, notes))

    # Set default demo monthly budget for current month & year
    cursor.execute("""
        INSERT OR REPLACE INTO budgets (month, year, amount, is_demo)
        VALUES (?, ?, ?, 1)
    """, (today.month, today.year, 1500.00))

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized. Real user expenses are kept separate from demo data.")
