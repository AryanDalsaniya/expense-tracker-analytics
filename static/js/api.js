/**
 * API Client Module
 * Provides unified, promise-based methods for all backend Flask endpoints.
 * Automatically adapts between direct Flask serving (port 5000) and external dev servers (port 5500 / Live Server).
 */

const getApiBaseUrl = () => {
    // If already served directly by Flask (port 5000 or standard production web port)
    if (window.location.port === '5000' || (window.location.protocol.startsWith('http') && window.location.port === '')) {
        return '';
    }
    // Default fallback to local Flask backend
    return 'http://127.0.0.1:5000';
};

const API_BASE = getApiBaseUrl();

const API = {
    baseUrl: API_BASE,

    // Health check to verify backend status
    async checkHealth() {
        try {
            const res = await fetch(`${API_BASE}/api/health`, { cache: 'no-store' });
            return res.ok;
        } catch {
            return false;
        }
    },

    // -------------------------------------------------------------
    // Expenses
    // -------------------------------------------------------------
    async getExpenses(params = {}) {
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`${API_BASE}/api/expenses?${query}`);
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to fetch expenses');
        return data.data;
    },

    async getExpenseById(id) {
        const res = await fetch(`${API_BASE}/api/expenses/${id}`);
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Expense not found');
        return data.data;
    },

    async createExpense(expenseData) {
        const res = await fetch(`${API_BASE}/api/expenses`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(expenseData)
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to add expense');
        return data;
    },

    async updateExpense(id, expenseData) {
        const res = await fetch(`${API_BASE}/api/expenses/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(expenseData)
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to update expense');
        return data;
    },

    async deleteExpense(id) {
        const res = await fetch(`${API_BASE}/api/expenses/${id}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to delete expense');
        return data;
    },

    async seedDemoData() {
        const res = await fetch(`${API_BASE}/api/expenses/seed`, { method: 'POST' });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to seed sample data');
        return data;
    },

    async clearExpenses() {
        const res = await fetch(`${API_BASE}/api/expenses/clear`, { method: 'DELETE' });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to clear expenses');
        return data;
    },

    // -------------------------------------------------------------
    // Categories & Payment Methods
    // -------------------------------------------------------------
    async getCategories() {
        try {
            const res = await fetch(`${API_BASE}/api/categories`);
            const data = await res.json();
            return data.data || [];
        } catch {
            return [
                { name: "Food & Dining", color: "#f97316" },
                { name: "Groceries", color: "#10b981" },
                { name: "Transportation", color: "#3b82f6" },
                { name: "Entertainment", color: "#8b5cf6" },
                { name: "Shopping", color: "#ec4899" },
                { name: "Utilities & Bills", color: "#eab308" },
                { name: "Health & Fitness", color: "#06b6d4" },
                { name: "Education", color: "#6366f1" },
                { name: "Travel", color: "#14b8a6" },
                { name: "Miscellaneous", color: "#64748b" }
            ];
        }
    },

    async getPaymentMethods() {
        try {
            const res = await fetch(`${API_BASE}/api/payment-methods`);
            const data = await res.json();
            return data.data || [];
        } catch {
            return ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"];
        }
    },

    // -------------------------------------------------------------
    // Analytics & Budgets
    // -------------------------------------------------------------
    async getSummaryKPIs() {
        const res = await fetch(`${API_BASE}/api/analytics/summary`);
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const data = await res.json();
        if (!data.success) throw new Error('Failed to load KPIs');
        return data.data;
    },

    async getCategoryAnalytics(params = {}) {
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`${API_BASE}/api/analytics/categories?${query}`);
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const data = await res.json();
        if (!data.success) throw new Error('Failed to load category analytics');
        return data.data;
    },

    async getTrends() {
        const res = await fetch(`${API_BASE}/api/analytics/trends`);
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const data = await res.json();
        if (!data.success) throw new Error('Failed to load trends');
        return data.data;
    },

    async getPaymentAnalytics() {
        const res = await fetch(`${API_BASE}/api/analytics/payment-methods`);
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        const data = await res.json();
        if (!data.success) throw new Error('Failed to load payment analytics');
        return data.data;
    },

    async updateBudget(amount) {
        const res = await fetch(`${API_BASE}/api/budget`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount: parseFloat(amount) })
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to update budget');
        return data;
    }
};

window.API = API;
