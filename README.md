# 💸 SpendWise — Expense Tracker & Financial Analytics

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask%203.1-black.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Chart.js](https://img.shields.io/badge/Visualization-Chart.js-FF6384.svg?logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![TailwindCSS](https://img.shields.io/badge/UI-Tailwind%20CSS-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(7%2F7)-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> A full-stack personal finance web application that helps individuals track daily expenses, understand spending habits, and monitor monthly budgets through interactive visual analytics. Built with Python, Flask, SQLite, Chart.js, and Tailwind CSS.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [How It Works](#-how-it-works)
- [Project Architecture](#-project-architecture)
- [REST API Reference](#-rest-api-reference)
- [How to Run (Quick Start)](#-how-to-run-quick-start)
- [Automated Testing](#-automated-testing)
- [Tech Stack & Engineering Concepts](#-tech-stack--engineering-concepts)
- [Author](#-author)

---

## 📖 Overview

Instead of recording expenses in notebooks or flat spreadsheets, **SpendWise** provides a modern fintech dashboard experience:
- **Clean slate for users:** Your real tracker starts 100% empty, recording only the transactions you enter.
- **Isolated preview sandbox:** Reviewers can inspect 28 realistic sample transactions with rich charts without altering your personal data.
- **Real-time analytics:** Categorized breakdowns, outflow trendlines, payment mode distribution, and monthly budget health meters update instantly upon every transaction.

---

## 🌟 Key Features

### 1. 🛡️ Dual Workspace: Live Tracker vs. Demo Sandbox
- **100% Isolated Data:** Real expenses are stored in `expenses`, while demo preview records reside in `demo_expenses`.
- **Zero Pollution:** Clearing your tracker or adding real expenses never affects demo data; resetting demo samples never touches your personal records.
- **Smart Switching:** If you add an expense while browsing the demo sandbox, SpendWise automatically saves it to your personal tracker and switches you to **My Tracker** mode.

### 2. 📊 Interactive Visual Analytics
- **Category Doughnut Chart:** Real-time breakdown of spending across 10 categories (*Food & Dining, Groceries, Transportation, Utilities, Shopping, Entertainment, etc.*).
- **Spending Trends Timeline:** Dynamic line graphs with **Daily** (day-by-day outflow curve) and **Monthly** historical toggles.
- **Payment Modes Distribution:** Real-time percentage shares of payment methods (*UPI, Credit Card, Debit Card, Net Banking, Cash*).

### 3. 🎯 Flexible Budget Management
- **Custom Limits:** Enter any numerical or decimal budget limit (e.g. `$2,150.50`, `$3,000.00`).
- **Period-Specific:** Configure budgets for any custom month and year.
- **Health Indicators:** Automatic visual badges:
  - 🟢 **Healthy** (`<75%` spent)
  - 🟡 **Near Limit** (`75% – 100%` spent)
  - 🔴 **Exceeded** (`>100%` spent)

### 4. ⚡ Interactive KPI Summary Cards
All four dashboard summary cards function as interactive shortcut buttons:
- **Total Recorded:** Click anywhere on the card to view all lifetime transactions.
- **This Month:** Click to filter dashboard charts and the table to the active month.
- **Monthly Budget:** Click to open the budget adjustment modal.
- **Highest Expense:** Click to sort transaction history by amount descending.

### 5. 📝 Complete Transaction Management (CRUD)
- **Record Expenses:** Title, Amount, Category, Date, Payment Method, and optional Notes.
- **Date Constraints & Quick Presets:** Date picker is constrained up to today with quick preset buttons: `[Today]`, `[Yesterday]`, `[3d ago]`, and `[7d ago]`.
- **Search & Filters:** Real-time search query matching title/notes, category dropdown, payment mode dropdown, and sort ordering (newest, oldest, highest, lowest).
- **In-Place Actions:** Edit and Delete with confirmation modals.
- **CSV Data Export:** One-click download of transaction history formatted for Excel and Google Sheets.

---

## 💡 How It Works

### Application Flow & Data Lifecycle

```
[ User Interaction ] 
       │
       ▼
[ Frontend Controller (app.js & api.js) ]
       │
       ├── Mode Parameter ('live' vs 'demo')
       ▼
[ Flask RESTful API (app.py) ]
       │
       ├── Services Layer (ExpenseService & AnalyticsService)
       ▼
[ SQLite Database (expenses.db) ]
       ├── Table: expenses        (Real user transactions)
       ├── Table: demo_expenses   (28 sample preview transactions)
       ├── Table: budgets         (Budget thresholds per month/year/mode)
       └── Table: categories      (Category names, icons & colors)
```

1. **State Isolation:** Every request from `static/js/api.js` carries a `mode` parameter (`live` or `demo`). The backend routes queries to the corresponding table.
2. **Aggregations:** Statistical computations (daily averages, percentages, highest expense) are executed on the backend via optimized SQL queries and delivered through JSON payloads.
3. **Reactive UI:** Responses update Chart.js canvas instances and DOM elements in place without full page reloads.

---

## 🏗️ Project Architecture

```
Expense Tracker with Analytics/
├── app.py                      # Flask Application factory & REST API endpoints
├── run.py                      # Cross-platform Python launcher script
├── run.bat                     # Windows instant one-click launcher
├── config.py                   # Central configuration, default categories & payment modes
├── database.py                 # SQLite schema creation, migrations & demo seeder
├── requirements.txt            # Python dependencies (UTF-8 encoded)
├── README.md                   # Comprehensive project documentation
├── .gitignore                  # Git ignore rules (virtual environment, SQLite DB)
├── services/
│   ├── expense_service.py      # Expense CRUD logic, validation, pagination & CSV export
│   └── analytics_service.py    # Statistical aggregations, KPI computation & trend analysis
├── static/
│   ├── css/
│   │   └── style.css           # Glassmorphism dark-mode UI styling & custom animations
│   └── js/
│       ├── api.js              # Fetch-based API client with automatic mode routing
│       ├── charts.js           # Chart.js initialization & responsive updates
│       └── app.js              # State management, event bindings & UI controller
├── templates/
│   └── index.html              # Responsive single-page fintech dashboard (Flask template)
├── tests/
│   └── test_tracker.py         # Automated unit and integration test suite
└── index.html                  # Standalone preview template (Live Server compatible)
```

---

## 📡 REST API Reference

All data endpoints accept an optional query parameter `mode=live` (default) or `mode=demo`.

| Method | Endpoint | Query / Body Parameters | Description |
|---|---|---|---|
| `GET` | `/` | — | Serves the web dashboard UI |
| `GET` | `/api/health` | — | API health check status |
| `GET` | `/api/categories` | — | Retrieve categories with icons and color codes |
| `GET` | `/api/payment-methods` | — | List supported payment methods |
| `GET` | `/api/expenses` | `mode`, `search`, `category`, `payment_method`, `sort_by`, `order`, `limit`, `offset`, `start_date`, `end_date` | Filter, search, and paginate transactions |
| `GET` | `/api/expenses/<id>` | `mode` | Fetch single expense details |
| `POST` | `/api/expenses` | `{ title, amount, category, date, payment_method, notes }` | Record a new expense (always saved to live table) |
| `PUT` | `/api/expenses/<id>` | `{ title, amount, category, date, payment_method, notes }` | Update an existing expense record |
| `DELETE` | `/api/expenses/<id>` | — | Delete an expense record |
| `POST` | `/api/expenses/seed` | — | Reset sample records in demo sandbox |
| `DELETE` | `/api/expenses/clear` | — | Clear real user expenses to start clean |
| `GET` | `/api/expenses/export` | `mode` | Download transactions as CSV attachment |
| `GET` | `/api/analytics/summary` | `mode`, `month`, `year` | High-level KPIs (Total, Monthly, Daily Avg, Budget) |
| `GET` | `/api/analytics/categories` | `mode`, `month`, `year`, `start_date`, `end_date` | Category-wise spending breakdown |
| `GET` | `/api/analytics/trends` | `mode`, `month`, `year` | Daily and monthly outflow trends |
| `GET` | `/api/analytics/payment-methods` | `mode`, `month`, `year` | Outflow distribution by payment mode |
| `POST` | `/api/budget` | `{ amount, month, year, is_demo }` | Set or update monthly budget limit |

---

## 🚀 How to Run (Quick Start)

### Prerequisites
- **Python 3.10+** installed ([Download Python](https://www.python.org/downloads/))
- **Git** installed ([Download Git](https://git-scm.com/downloads))

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/AryanDalsaniya/expense-tracker-analytics.git
cd expense-tracker-analytics
```

---

### Step 2: Set Up Virtual Environment

**On Windows (PowerShell / Command Prompt):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

### Step 4: Launch the Application

You can start the app using any of the following methods:

#### Method A — One-Click Launcher (Windows):
Double-click `run.bat` in File Explorer, or run in terminal:
```cmd
run.bat
```

#### Method B — Cross-Platform Launcher:
```bash
python run.py
```

#### Method C — Direct Flask Execution:
```bash
python app.py
```

Once started, open your browser and navigate to:
```
http://127.0.0.1:5000
```

> **Note for VS Code Live Server users:** If you prefer viewing via Live Server (port 5500), keep `python app.py` running in the background. The app automatically detects port 5500 and bridges all API calls via CORS.

---

## 🧪 Automated Testing

SpendWise includes an automated test suite verifying data isolation, CRUD operations, budget updates, and CSV generation:

```bash
python -m unittest discover -s tests
```

### Test Coverage Summary:
- `test_01_live_mode_empty_slate`: Verifies live tracker initializes with 0 records.
- `test_02_demo_mode_isolation`: Confirms demo sandbox isolates 28 sample preview transactions.
- `test_03_live_kpis_when_empty`: Checks KPIs report `$0.00` total and null highest expense when empty.
- `test_04_custom_budget_any_value`: Verifies custom decimal budget limits can be saved and retrieved.
- `test_05_create_and_recalculate_analytics`: Validates that adding an expense updates KPIs, categories, and trends.
- `test_06_clear_and_seed_isolation`: Ensures clearing live data leaves demo data intact, and seeding demo leaves live data clean.
- `test_07_export_csv`: Validates CSV export content and attachment headers.

---

## 🛠️ Tech Stack & Engineering Concepts

| Layer | Technologies & Skills |
|---|---|
| **Frontend** | HTML5 Semantic Elements, Tailwind CSS (Dark Mode), Chart.js 4.4, Vanilla JavaScript (ES6+), Fetch API, DOM manipulation |
| **Backend** | Python 3, Flask 3.1 (Application Factory pattern, CORS middleware, REST API standards, error handling) |
| **Database** | SQLite3, Schema Migrations, Context Managers (`@contextmanager`), Parameterized SQL Queries, Foreign Key integrity |
| **Testing** | Python `unittest`, Mock HTTP client (`test_client`), Temporary database isolation (`tempfile`) |
| **DevOps & Tooling** | Git, Conventional Commits, Cross-platform launch scripts (`run.bat`, `run.py`) |

---

## 👤 Author

**Aryan Dalsaniya**
- GitHub: [@AryanDalsaniya](https://github.com/AryanDalsaniya)
- Repository: [expense-tracker-analytics](https://github.com/AryanDalsaniya/expense-tracker-analytics)
- Email: aryanpatel1460@gmail.com
