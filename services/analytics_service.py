from datetime import datetime, timedelta
import calendar
from database import get_db_connection

class AnalyticsService:

    @staticmethod
    def get_summary_kpis(mode="live", month=None, year=None, period_mode="month"):
        """Compute high-level Key Performance Indicators (KPIs) for the dashboard, respecting mode and period."""
        table = "demo_expenses" if mode == "demo" else "expenses"
        is_demo_val = 1 if mode == "demo" else 0

        now = datetime.now()
        target_year = int(year) if year else now.year
        target_month = int(month) if month else now.month

        month_prefix = f"{target_year:04d}-{target_month:02d}%"
        today_str = now.strftime("%Y-%m-%d")
        _, num_days = calendar.monthrange(target_year, target_month)
        month_label = f"{calendar.month_name[target_month]} {target_year}"

        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 1. Total Lifetime Spending & Count
            cursor.execute(f"SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count FROM {table}")
            lifetime = cursor.fetchone()
            total_spent = float(lifetime["total"])
            total_transactions = int(lifetime["count"])

            # 2. Selected Month Spending & Count
            cursor.execute(f"SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count FROM {table} WHERE date LIKE ?", (month_prefix,))
            monthly = cursor.fetchone()
            monthly_spent = float(monthly["total"])
            monthly_transactions = int(monthly["count"])

            # 3. Today's Spending
            cursor.execute(f"SELECT COALESCE(SUM(amount), 0) as total FROM {table} WHERE date = ?", (today_str,))
            today_spent = float(cursor.fetchone()["total"])

            # 4. Highest Expense (for the selected month, or lifetime in all-time view)
            cursor.execute(f"SELECT title, amount, category, date FROM {table} WHERE date LIKE ? ORDER BY amount DESC LIMIT 1", (month_prefix,))
            highest_in_month = cursor.fetchone()

            cursor.execute(f"SELECT title, amount, category, date FROM {table} ORDER BY amount DESC LIMIT 1")
            highest_lifetime = cursor.fetchone()

            if period_mode == "all":
                highest_expense = dict(highest_lifetime) if highest_lifetime else None
            else:
                highest_expense = dict(highest_in_month) if highest_in_month else (dict(highest_lifetime) if highest_lifetime else None)

            # 5. Average Daily Spend (for selected month)
            if target_year == now.year and target_month == now.month:
                days_passed = max(now.day, 1)
            else:
                days_passed = max(num_days, 1)

            daily_avg = monthly_spent / days_passed if monthly_spent > 0 else 0.0

            # 6. Budget Information for selected month/year and mode
            cursor.execute("SELECT amount FROM budgets WHERE month = ? AND year = ? AND is_demo = ?", (target_month, target_year, is_demo_val))
            budget_row = cursor.fetchone()

            if budget_row:
                monthly_budget = float(budget_row["amount"])
            else:
                cursor.execute("SELECT amount FROM budgets WHERE is_demo = ? ORDER BY year DESC, month DESC LIMIT 1", (is_demo_val,))
                recent_budget = cursor.fetchone()
                monthly_budget = float(recent_budget["amount"]) if recent_budget else 1500.00
            
            remaining_budget = monthly_budget - monthly_spent
            budget_percent = round((monthly_spent / monthly_budget) * 100, 1) if monthly_budget > 0 else 0

            if monthly_budget == 0:
                budget_status = "No Budget"
                budget_status_color = "slate"
            elif budget_percent < 75:
                budget_status = "Healthy"
                budget_status_color = "emerald"
            elif budget_percent <= 100:
                budget_status = "Near Limit"
                budget_status_color = "amber"
            else:
                budget_status = "Exceeded"
                budget_status_color = "rose"

            return {
                "period": {
                    "month": target_month,
                    "year": target_year,
                    "label": month_label
                },
                "mode": mode,
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
    def get_category_breakdown(mode="live", start_date=None, end_date=None, month=None, year=None):
        """Aggregate total spending and percentage distribution by category from active mode table."""
        table = "demo_expenses" if mode == "demo" else "expenses"

        if month and year:
            month = int(month)
            year = int(year)
            _, num_days = calendar.monthrange(year, month)
            start_date = f"{year:04d}-{month:02d}-01"
            end_date = f"{year:04d}-{month:02d}-{num_days:02d}"

        query = f"""
            SELECT e.category,
                   COALESCE(SUM(e.amount), 0) as total_amount,
                   COUNT(e.id) as count,
                   COALESCE(c.color, '#64748b') as color,
                   COALESCE(c.icon, 'tag') as icon
            FROM {table} e
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
                "total_amount": round(total_sum, 2),
                "mode": mode
            }

    @staticmethod
    def get_monthly_trends(mode="live", months_back=6):
        """Calculate month-by-month spending trends for the last N months from active mode table."""
        table = "demo_expenses" if mode == "demo" else "expenses"
        now = datetime.now()
        months_list = []
        
        for i in range(months_back - 1, -1, -1):
            y = now.year
            m = now.month - i
            while m <= 0:
                m += 12
                y -= 1
            dt = datetime(y, m, 1)
            months_list.append((dt.year, dt.month, dt.strftime("%b %Y"), f"{dt.year:04d}-{dt.month:02d}"))

        with get_db_connection() as conn:
            cursor = conn.cursor()
            results = []

            for year, month, label, key in months_list:
                cursor.execute(f"""
                    SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count
                    FROM {table}
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
    def get_daily_trends(mode="live", month=None, year=None):
        """Retrieve daily spending data for chosen month from active mode table."""
        table = "demo_expenses" if mode == "demo" else "expenses"
        now = datetime.now()
        target_year = int(year) if year else now.year
        target_month = int(month) if month else now.month
        month_prefix = f"{target_year:04d}-{target_month:02d}%"

        _, num_days = calendar.monthrange(target_year, target_month)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT date, COALESCE(SUM(amount), 0) as total, COUNT(*) as count
                FROM {table}
                WHERE date LIKE ?
                GROUP BY date
                ORDER BY date ASC
            """, (month_prefix,))
            rows = cursor.fetchall()
            spending_by_date = {r["date"]: round(float(r["total"]), 2) for r in rows}

        days = []
        max_day = now.day if (target_year == now.year and target_month == now.month) else num_days

        for day in range(1, num_days + 1):
            date_str = f"{target_year:04d}-{target_month:02d}-{day:02d}"
            if day > max_day:
                break
            days.append({
                "date": date_str,
                "day": day,
                "label": f"{day} {calendar.month_abbr[target_month]}",
                "amount": spending_by_date.get(date_str, 0.0)
            })

        return days

    @staticmethod
    def get_payment_breakdown(mode="live", month=None, year=None):
        """Compute spending totals grouped by payment method from active mode table."""
        table = "demo_expenses" if mode == "demo" else "expenses"
        query = f"""
            SELECT payment_method,
                   COALESCE(SUM(amount), 0) as total,
                   COUNT(*) as count
            FROM {table}
            WHERE 1=1
        """
        params = []
        if month and year:
            query += " AND date LIKE ?"
            params.append(f"{int(year):04d}-{int(month):02d}%")

        query += " GROUP BY payment_method ORDER BY total DESC"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
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
    def set_monthly_budget(amount, month=None, year=None, is_demo=0):
        """Set or update monthly budget for given month/year."""
        now = datetime.now()
        month = int(month) if month else now.month
        year = int(year) if year else now.year
        is_demo_val = 1 if is_demo else 0

        try:
            budget_amount = float(amount)
            if budget_amount <= 0:
                raise ValueError("Budget must be a positive number.")
        except (ValueError, TypeError):
            raise ValueError("Invalid budget amount.")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM budgets WHERE month = ? AND year = ? AND is_demo = ?", (month, year, is_demo_val))
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE budgets SET amount = ? WHERE id = ?", (budget_amount, row["id"]))
            else:
                cursor.execute(
                    "INSERT INTO budgets (month, year, amount, is_demo) VALUES (?, ?, ?, ?)",
                    (month, year, budget_amount, is_demo_val)
                )
            conn.commit()

        return {"month": month, "year": year, "amount": budget_amount, "is_demo": is_demo_val}
