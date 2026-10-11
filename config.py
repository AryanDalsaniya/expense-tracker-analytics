import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "expense-tracker-secret-key-portfolio-2026")
    DATABASE_PATH = os.path.join(BASE_DIR, "data", "expenses.db")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    DEFAULT_CATEGORIES = [
        {"name": "Food & Dining", "color": "#f97316", "icon": "utensils"},
        {"name": "Groceries", "color": "#10b981", "icon": "shopping-cart"},
        {"name": "Transportation", "color": "#3b82f6", "icon": "car"},
        {"name": "Entertainment", "color": "#8b5cf6", "icon": "film"},
        {"name": "Shopping", "color": "#ec4899", "icon": "shopping-bag"},
        {"name": "Utilities & Bills", "color": "#eab308", "icon": "zap"},
        {"name": "Health & Fitness", "color": "#06b6d4", "icon": "heart-pulse"},
        {"name": "Education", "color": "#6366f1", "icon": "graduation-cap"},
        {"name": "Travel", "color": "#14b8a6", "icon": "plane"},
        {"name": "Miscellaneous", "color": "#64748b", "icon": "more-horizontal"},
    ]

    DEFAULT_PAYMENT_METHODS = [
        "UPI",
        "Credit Card",
        "Debit Card",
        "Cash",
        "Net Banking"
    ]

