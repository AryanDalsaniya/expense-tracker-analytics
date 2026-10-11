# 💸 SpendWise — Expense Tracker & Financial Analytics

[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask%203.1-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Chart.js](https://img.shields.io/badge/Visualization-Chart.js-FF6384.svg?logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![TailwindCSS](https://img.shields.io/badge/UI-Tailwind%20CSS-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> A modern, responsive personal finance and expense analytics web application. Move beyond manual spreadsheets into an interactive dashboard featuring real-time financial metrics, category breakdown charts, monthly budget health tracking, and CSV data export.

---

## 🌟 Key Features

### 1. 📊 Interactive Visual Analytics
- **Category Doughnut Chart:** Real-time percentage distribution of spending across 10 categories (Food, Transportation, Utilities, Shopping, etc.).
- **Spending Trends (Daily & Monthly):** Interactive line graphs tracking daily outflow for the current month and month-by-month history.
- **Payment Method Share:** Visual breakdown of transactions paid via UPI, Credit Card, Debit Card, Net Banking, and Cash.

### 2. 🎯 Budget Health & Alerts
- Set custom monthly spending limits.
- Real-time progress bar reflecting consumed vs. remaining budget.
- Automatic status pills: **Healthy (<75%)**, **Near Limit (75-100%)**, and **Exceeded (>100%)**.

### 3. 📝 Complete Expense Management (CRUD)
- Record transactions with Title, Amount, Category, Date, Payment Mode, and Notes.
- In-place Edit and Delete with confirmation modals.
- Real-time search by title or description.
- Multi-field filters: filter by category, payment method, and sort by date or amount.
- Pagination for clean browsing through large datasets.

### 4. 🚀 Demo & Data Portability
- **One-Click Demo Data:** Load 28+ realistic sample transactions spanning 40 days to immediately showcase rich charts.
- **Export to CSV:** Download all transaction history directly to an Excel/spreadsheet-compatible CSV file.

---

## 🏗️ Architecture & Project Structure

The project follows a clean, modular architecture with clear separation between routing, business logic, data persistence, and UI presentation:

```
Expense Tracker with Analytics/
├── app.py                      # Flask Application factory & RESTful API routes
├── config.py                   # Central configuration, default categories & payment modes
├── database.py                 # SQLite schema creation, connection manager & demo seeder
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules (virtual environment, SQLite DB)
├── services/
│   ├── expense_service.py      # Expense CRUD logic, validation, pagination, CSV generation
│   └── analytics_service.py    # Statistical aggregations, KPI metrics, trend analysis
├── static/
│   ├── css/
│   │   └── style.css           # Glassmorphism dark-mode UI styling & custom animations
│   └── js/
│       ├── api.js              # Fetch-based API client
│       ├── charts.js           # Chart.js initialization & responsive updates
│       └── app.js              # State management, event bindings, and UI controller
└── templates/
    └── index.html              # Responsive single-page fintech dashboard
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Renders the web dashboard UI |
| `GET` | `/api/categories` | Retrieve all categories with icons and color codes |
| `GET` | `/api/payment-methods` | List supported payment methods |
| `GET` | `/api/expenses` | Filter, search, and paginate expense records |
| `GET` | `/api/expenses/<id>` | Fetch single expense details |
| `POST` | `/api/expenses` | Add a new expense record |
| `PUT` | `/api/expenses/<id>` | Update an existing expense record |
| `DELETE` | `/api/expenses/<id>` | Delete an expense record |
| `POST` | `/api/expenses/seed` | Seed realistic demo transactions |
| `DELETE` | `/api/expenses/clear` | Clear all expense records |
| `GET` | `/api/expenses/export` | Download transaction dataset as CSV |
| `GET` | `/api/analytics/summary` | High-level KPIs (Total, Monthly, Daily Avg, Budget) |
| `GET` | `/api/analytics/categories`| Category-wise spending aggregations |
| `GET` | `/api/analytics/trends` | Daily and monthly spending trends |
| `GET` | `/api/analytics/payment-methods` | Spending grouped by payment mode |
| `POST` | `/api/budget` | Set or update monthly budget limit |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ installed
- Git installed

### 1. Clone the Repository
```bash
git clone https://github.com/AryanDalsaniya/expense-tracker-analytics.git
cd "expense-tracker-analytics"
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🛠️ Tech Stack & Skills Demonstrated

- **Frontend:** Semantic HTML5, CSS3, Tailwind CSS, Chart.js, Vanilla JavaScript (ES6+ Modules, Fetch API, DOM manipulation).
- **Backend:** Python, Flask (Application Factory, REST API architecture, HTTP status codes).
- **Database:** SQLite3, SQL DDL/DML, parameter-binding, table constraints, aggregations.
- **Data Analytics:** Grouping, time-series aggregation, budget percentage tracking.
- **Version Control:** Git, clean atomic commit conventions.

---

## 👤 Author

**Aryan Dalsaniya**
- GitHub: [@AryanDalsaniya](https://github.com/AryanDalsaniya)
- Email: aryanpatel1460@gmail.com

