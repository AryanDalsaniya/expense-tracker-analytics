import os
import threading
import webbrowser
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from config import Config
from database import init_db
from services.expense_service import ExpenseService
from services.analytics_service import AnalyticsService

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for cross-origin development (e.g. Live Server, Vite, port 5500)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize database on app startup (do not auto-seed demo data, keep empty for user)
    with app.app_context():
        init_db(seed_if_empty=False)

    # -----------------------------------------
    # Frontend Routes
    # -----------------------------------------
    @app.route("/")
    def index():
        return render_template("index.html")

    # -----------------------------------------
    # Expense Endpoints
    # -----------------------------------------
    @app.route("/api/categories", methods=["GET"])
    def get_categories():
        categories = ExpenseService.get_categories()
        return jsonify({"success": True, "data": categories})

    @app.route("/api/payment-methods", methods=["GET"])
    def get_payment_methods():
        methods = ExpenseService.get_payment_methods()
        return jsonify({"success": True, "data": methods})

    @app.route("/api/expenses", methods=["GET"])
    def get_expenses():
        search = request.args.get("search", "")
        category = request.args.get("category", "")
        payment_method = request.args.get("payment_method", "")
        start_date = request.args.get("start_date", "")
        end_date = request.args.get("end_date", "")
        sort_by = request.args.get("sort_by", "date")
        order = request.args.get("order", "DESC")
        limit = request.args.get("limit", 10)
        offset = request.args.get("offset", 0)

        result = ExpenseService.get_all_expenses(
            search=search,
            category=category,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            order=order,
            limit=limit,
            offset=offset
        )
        return jsonify({"success": True, "data": result})

    @app.route("/api/expenses/<int:expense_id>", methods=["GET"])
    def get_expense(expense_id):
        expense = ExpenseService.get_expense_by_id(expense_id)
        if not expense:
            return jsonify({"success": False, "error": "Expense not found"}), 404
        return jsonify({"success": True, "data": expense})

    @app.route("/api/expenses", methods=["POST"])
    def add_expense():
        data = request.get_json() or {}
        try:
            created = ExpenseService.create_expense(data)
            return jsonify({"success": True, "message": "Expense added successfully", "data": created}), 201
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400
        except Exception as e:
            return jsonify({"success": False, "error": "An unexpected error occurred"}), 500

    @app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
    def update_expense(expense_id):
        data = request.get_json() or {}
        try:
            updated = ExpenseService.update_expense(expense_id, data)
            if not updated:
                return jsonify({"success": False, "error": "Expense not found"}), 404
            return jsonify({"success": True, "message": "Expense updated successfully", "data": updated})
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400
        except Exception as e:
            return jsonify({"success": False, "error": "An unexpected error occurred"}), 500

    @app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
    def delete_expense(expense_id):
        success = ExpenseService.delete_expense(expense_id)
        if not success:
            return jsonify({"success": False, "error": "Expense not found"}), 404
        return jsonify({"success": True, "message": "Expense deleted successfully"})

    @app.route("/api/expenses/seed", methods=["POST"])
    def seed_data():
        ExpenseService.seed_demo_data()
        return jsonify({"success": True, "message": "Sample portfolio data loaded successfully"})

    @app.route("/api/expenses/clear", methods=["DELETE"])
    def clear_expenses():
        ExpenseService.clear_all_expenses()
        return jsonify({"success": True, "message": "All expense records cleared"})

    @app.route("/api/expenses/export", methods=["GET"])
    def export_csv():
        csv_data = ExpenseService.export_csv()
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=expenses_export.csv"}
        )

    # -----------------------------------------
    # Analytics Endpoints
    # -----------------------------------------
    @app.route("/api/analytics/summary", methods=["GET"])
    def get_summary_kpis():
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)
        kpis = AnalyticsService.get_summary_kpis(month=month, year=year)
        return jsonify({"success": True, "data": kpis})

    @app.route("/api/analytics/categories", methods=["GET"])
    def get_category_analytics():
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)
        start_date = request.args.get("start_date", "")
        end_date = request.args.get("end_date", "")
        breakdown = AnalyticsService.get_category_breakdown(start_date=start_date, end_date=end_date, month=month, year=year)
        return jsonify({"success": True, "data": breakdown})

    @app.route("/api/analytics/trends", methods=["GET"])
    def get_trends():
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)
        monthly = AnalyticsService.get_monthly_trends()
        daily = AnalyticsService.get_daily_trends(month=month, year=year)
        return jsonify({"success": True, "data": {"monthly": monthly, "daily": daily}})

    @app.route("/api/analytics/payment-methods", methods=["GET"])
    def get_payment_methods_analytics():
        month = request.args.get("month", type=int)
        year = request.args.get("year", type=int)
        methods = AnalyticsService.get_payment_breakdown(month=month, year=year)
        return jsonify({"success": True, "data": methods})

    @app.route("/api/budget", methods=["POST"])
    def update_budget():
        data = request.get_json() or {}
        amount = data.get("amount")
        month = data.get("month")
        year = data.get("year")
        try:
            res = AnalyticsService.set_monthly_budget(amount, month, year)
            return jsonify({"success": True, "message": "Monthly budget updated", "data": res})
        except ValueError as e:
            return jsonify({"success": False, "error": str(e)}), 400

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"success": True, "status": "healthy", "service": "SpendWise API"})

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*60)
    print(f"  🚀 SpendWise Financial Analytics Server")
    print(f"  📍 Local URL: http://127.0.0.1:{port}")
    print(f"  📊 API Health: http://127.0.0.1:{port}/api/health")
    print("="*60 + "\n")
    
    # Auto open browser only in main process (not reload thread)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not Config.DEBUG:
        threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()

    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)

