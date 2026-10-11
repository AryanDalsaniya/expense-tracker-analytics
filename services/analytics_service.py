from datetime import datetime, timedelta
import calendar
from database import get_db_connection

class AnalyticsService:

    @staticmethod
    def get_summary_kpis():
        """Compute high-level Key Performance Indicators (KPIs) for the dashboard."""
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        today_str = now.strftime("%Y-%m-%d")
        month_prefix = f"{current_year:04d}-{current_month:02d}%"

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 1. Total Lifetime Spending & Count
            cursor.execute("SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count FROM expenses")
            lifetime = cursor.fetchone()
            total_spent = float(lifetime["total"])
            total_transactions = int(lifetime["count"])

            # 2. Current Month Spending & Count
            cursor.execute("SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count FROM expenses WHERE date LIKE ?", (month_prefix,))
            monthly = cursor.fetchone()
            monthly_spent = float(monthly["total"])
            monthly_transactions = int(monthly["count"])

            # 3. Today's Spending
            cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE date = ?", (today_str,))
            today_spent = float(cursor.fetchone()["total"])

            # 4. Highest Single Expense
            cursor.execute("SELECT title, amount, category, date FROM expenses ORDER BY amount DESC LIMIT 1")
            highest = cursor.fetchone()
            highest_expense = dict(highest) if highest else None

            # 5. Average Daily Spend (for current month)
            days_passed = max(now.day, 1)
            daily_avg = monthly_spent / days_passed

            # 6. Budget Information
            cursor.execute("SELECT amount FROM budgets WHERE month = ? AND year = ?", (current_month, current_year))
            budget_row = cursor.fetchone()
            monthly_budget = float(budget_row["amount"]) if budget_row else 1500.00
            
            remaining_budget = monthly_budget - monthly_spent
            budget_percent = round((monthly_spent / monthly_budget) * 100, 1) if monthly_budget > 0 else 0

            if budget_percent < 75:
                budget_status = "Healthy"
                budget_status_color = "emerald"
            elif budget_percent <= 100:
                budget_status = "Near Limit"
                budget_status_color = "amber"
            else:
                budget_status = "Exceeded"
                budget_status_color = "rose"

            return {
                "total_spent": round(total_spent, 2),
                "total_transactions": total_transactions,
                "monthly_spent": round(monthly_spent, 2),
                "monthly_transactions": monthly_transactions,
                "today_spent": round(today_spent, 2),
                "daily_avg": round(daily_avg, 2),
                "highest_expense": highest_expense,
                "budget": {
                    "limit": round(monthly_budget, 2),
                    "spent": round(monthly_spent, 2),
                    "remaining": round(remaining_budget, 2),
                    "percentage": min(budget_percent, 100),
                    "raw_percentage": budget_percent,
                    "status": budget_status,
                    "status_color": budget_status_color
                }
            }

    @staticmethod
    def get_category_breakdown(start_date=None, end_date=None):
        """Aggregate total spending and percentage distribution by category."""
        query = """
            SELECT e.category,
                   COALESCE(SUM(e.amount), 0) as total_amount,
                   COUNT(e.id) as count,
                   COALESCE(c.color, '#64748b') as color,
                   COALESCE(c.icon, 'tag') as icon
            FROM expenses e
            LEFT JOIN categories c ON e.category = c.name
            WHERE 1=1
        """
        params = []
        if start_date:
            query += " AND e.date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND e.date <= ?"
            params.append(end_date)

        query += " GROUP BY e.category ORDER BY total_amount DESC"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            total_sum = sum(float(r["total_amount"]) for r in rows)

            categories = []
            for r in rows:
                amount = float(r["total_amount"])
                percentage = round((amount / total_sum * 100), 1) if total_sum > 0 else 0
                categories.append({
                    "name": r["category"],
                    "amount": round(amount, 2),
                    "count": r["count"],
                    "percentage": percentage,
                    "color": r["color"],
                    "icon": r["icon"]
                })

            return {
                "categories": categories,
                "total_amount": round(total_sum, 2)
            }

    @staticmethod
    def get_monthly_trends(months_back=6):
        """Calculate month-by-month spending trends for the last N months."""
        now = datetime.now()
        months_list = []
        
        # Build list of year-month keys
        for i in range(months_back - 1, -1, -1):
            dt = (now.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
            months_list.append((dt.year, dt.month, dt.strftime("%b %Y"), f"{dt.year:04d}-{dt.month:02d}"))

        with get_db_connection() as conn:
            cursor = conn.cursor()
            results = []

            for year, month, label, key in months_list:
                cursor.execute("""
                    SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count
                    FROM expenses
                    WHERE date LIKE ?
                """, (f"{key}%",))
                row = cursor.fetchone()
                results.append({
                    "year": year,
                    "month": month,
                    "label": label,
                    "key": key,
                    "total": round(float(row["total"]), 2),
                    "count": int(row["count"])
                })

            return results

    @staticmethod
    def get_daily_trends():
        """Retrieve daily spending data for the current active month."""
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        month_prefix = f"{current_year:04d}-{current_month:02d}%"

        _, num_days = calendar.monthrange(current_year, current_month)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date, COALESCE(SUM(amount), 0) as total, COUNT(*) as count
                FROM expenses
                WHERE date LIKE ?
                GROUP BY date
                ORDER BY date ASC
            """, (month_prefix,))
            rows = cursor.fetchall()
            spending_by_date = {r["date"]: round(float(r["total"]), 2) for r in rows}

        days = []
        for day in range(1, num_days + 1):
            date_str = f"{current_year:04d}-{current_month:02d}-{day:02d}"
            # Only up to today if it's the current month
            if day > now.day:
                break
            days.append({
                "date": date_str,
                "day": day,
                "label": f"{day} {calendar.month_abbr[current_month]}",
                "amount": spending_by_date.get(date_str, 0.0)
            })

        return days

    @staticmethod
    def get_payment_breakdown():
        """Compute spending totals grouped by payment method."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT payment_method,
                       COALESCE(SUM(amount), 0) as total,
                       COUNT(*) as count
                FROM expenses
                GROUP BY payment_method
                ORDER BY total DESC
            """)
            rows = cursor.fetchall()
            total_sum = sum(float(r["total"]) for r in rows)

            return [
                {
                    "method": r["payment_method"],
                    "total": round(float(r["total"]), 2),
                    "count": int(r["count"]),
                    "percentage": round((float(r["total"]) / total_sum * 100), 1) if total_sum > 0 else 0
                }
                for r in rows
            ]

    @staticmethod
    def set_monthly_budget(amount, month=None, year=None):
        """Set or update monthly budget for given month/year."""
        now = datetime.now()
        month = month or now.month
        year = year or now.year

        try:
            budget_amount = float(amount)
            if budget_amount <= 0:
                raise ValueError("Budget must be a positive number.")
        except (ValueError, TypeError):
            raise ValueError("Invalid budget amount.")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO budgets (month, year, amount)
                VALUES (?, ?, ?)
                ON CONFLICT(month, year) DO UPDATE SET amount = excluded.amount
            """, (month, year, budget_amount))
            conn.commit()

        return {"month": month, "year": year, "amount": budget_amount}

