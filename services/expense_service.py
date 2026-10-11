import csv
import io
from datetime import datetime
from database import get_db_connection, seed_sample_data
from config import Config

class ExpenseService:

    @staticmethod
    def get_categories():
        """Retrieve all available expense categories with colors and icons."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, color, icon FROM categories ORDER BY name ASC")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_payment_methods():
        """Retrieve all supported payment methods."""
        return Config.DEFAULT_PAYMENT_METHODS

    @staticmethod
    def get_all_expenses(search=None, category=None, payment_method=None,
                         start_date=None, end_date=None, sort_by="date",
                         order="DESC", limit=None, offset=None):
        """Retrieve filtered, sorted, and paginated expense transactions."""
        query = "SELECT e.id, e.title, e.amount, e.category, e.date, e.payment_method, e.notes, e.created_at, c.color as category_color, c.icon as category_icon FROM expenses e LEFT JOIN categories c ON e.category = c.name WHERE 1=1"
        params = []

        if search:
            query += " AND (e.title LIKE ? OR e.notes LIKE ?)"
            params.extend([f"%{search.strip()}%", f"%{search.strip()}%"])

        if category and category != "all":
            query += " AND e.category = ?"
            params.append(category)

        if payment_method and payment_method != "all":
            query += " AND e.payment_method = ?"
            params.append(payment_method)

        if start_date:
            query += " AND e.date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND e.date <= ?"
            params.append(end_date)

        allowed_sort = {"date": "e.date", "amount": "e.amount", "title": "e.title", "id": "e.id"}
        sort_column = allowed_sort.get(sort_by, "e.date")
        sort_direction = "DESC" if order.upper() == "DESC" else "ASC"

        query += f" ORDER BY {sort_column} {sort_direction}, e.id DESC"

        if limit is not None:
            query += " LIMIT ?"
            params.append(int(limit))
            if offset is not None:
                query += " OFFSET ?"
                params.append(int(offset))

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Count total matching records for pagination
            count_query = "SELECT COUNT(*) as total FROM expenses e WHERE 1=1"
            count_params = []
            if search:
                count_query += " AND (e.title LIKE ? OR e.notes LIKE ?)"
                count_params.extend([f"%{search.strip()}%", f"%{search.strip()}%"])
            if category and category != "all":
                count_query += " AND e.category = ?"
                count_params.append(category)
            if payment_method and payment_method != "all":
                count_query += " AND e.payment_method = ?"
                count_params.append(payment_method)
            if start_date:
                count_query += " AND e.date >= ?"
                count_params.append(start_date)
            if end_date:
                count_query += " AND e.date <= ?"
                count_params.append(end_date)

            cursor.execute(count_query, count_params)
            total_count = cursor.fetchone()["total"]

            return {
                "expenses": [dict(r) for r in rows],
                "total_count": total_count
            }

    @staticmethod
    def get_expense_by_id(expense_id):
        """Fetch single expense transaction by ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.*, c.color as category_color, c.icon as category_icon
                FROM expenses e
                LEFT JOIN categories c ON e.category = c.name
                WHERE e.id = ?
            """, (expense_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def create_expense(data):
        """Validate and insert a new expense transaction."""
        title = data.get("title", "").strip()
        category = data.get("category", "").strip()
        date = data.get("date", "").strip()
        payment_method = data.get("payment_method", "Debit Card").strip()
        notes = data.get("notes", "").strip()

        try:
            amount = float(data.get("amount", 0))
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid positive number.")

        if not title:
            raise ValueError("Expense title is required.")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        if not category:
            raise ValueError("Expense category is required.")
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO expenses (title, amount, category, date, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, amount, category, date, payment_method, notes))
            new_id = cursor.lastrowid
            conn.commit()

        return ExpenseService.get_expense_by_id(new_id)

    @staticmethod
    def update_expense(expense_id, data):
        """Validate and update an existing expense transaction."""
        existing = ExpenseService.get_expense_by_id(expense_id)
        if not existing:
            return None

        title = data.get("title", existing["title"]).strip()
        category = data.get("category", existing["category"]).strip()
        date = data.get("date", existing["date"]).strip()
        payment_method = data.get("payment_method", existing["payment_method"]).strip()
        notes = data.get("notes", existing["notes"]).strip()

        try:
            amount = float(data.get("amount", existing["amount"]))
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid positive number.")

        if not title:
            raise ValueError("Expense title cannot be empty.")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE expenses
                SET title = ?, amount = ?, category = ?, date = ?, payment_method = ?, notes = ?
                WHERE id = ?
            """, (title, amount, category, date, payment_method, notes, expense_id))
            conn.commit()

        return ExpenseService.get_expense_by_id(expense_id)

    @staticmethod
    def delete_expense(expense_id):
        """Delete an expense transaction by ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            affected = cursor.rowcount
            conn.commit()
            return affected > 0

    @staticmethod
    def clear_all_expenses():
        """Delete all recorded expenses."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses")
            conn.commit()
            return True

    @staticmethod
    def seed_demo_data():
        """Reset and seed realistic sample data."""
        seed_sample_data()
        return True

    @staticmethod
    def export_csv():
        """Export all expenses as formatted CSV."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, amount, category, date, payment_method, notes, created_at
                FROM expenses
                ORDER BY date DESC, id DESC
            """)
            rows = cursor.fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Title", "Amount", "Category", "Date", "Payment Method", "Notes", "Recorded At"])

        for row in rows:
            writer.writerow([
                row["id"],
                row["title"],
                f"{row['amount']:.2f}",
                row["category"],
                row["date"],
                row["payment_method"],
                row["notes"],
                row["created_at"]
            ])

        return output.getvalue()
