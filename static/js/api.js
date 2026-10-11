/**
 * API Client Module
 * Provides unified, promise-based methods for all backend Flask endpoints.
 */

const API = {
    // -------------------------------------------------------------
    // Expenses
    // -------------------------------------------------------------
    async getExpenses(params = {}) {
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`/api/expenses?${query}`);
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to fetch expenses');
        return data.data;
    },

    async getExpenseById(id) {
        const res = await fetch(`/api/expenses/${id}`);
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Expense not found');
        return data.data;
    },

    async createExpense(expenseData) {
        const res = await fetch('/api/expenses', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(expenseData)
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to add expense');
        return data;
    },

    async updateExpense(id, expenseData) {
        const res = await fetch(`/api/expenses/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(expenseData)
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to update expense');
        return data;
    },

    async deleteExpense(id) {
        const res = await fetch(`/api/expenses/${id}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to delete expense');
        return data;
    },

    async seedDemoData() {
        const res = await fetch('/api/expenses/seed', { method: 'POST' });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to seed sample data');
        return data;
    },

    async clearExpenses() {
        const res = await fetch('/api/expenses/clear', { method: 'DELETE' });
        const data = await res.json();
        if (!data.success) throw new Error(data.error || 'Failed to clear expenses');
        return data;
    },

    // -------------------------------------------------------------
    // Categories & Payment Methods
    // -------------------------------------------------------------
    async getCategories() {
        const res = await fetch('/api/categories');
        const data = await res.json();
        return data.data || [];
    },

    async getPaymentMethods() {
        const res = await fetch('/api/payment-methods');
        const data = await res.json();
        return data.data || [];
    },

    // -------------------------------------------------------------
    // Analytics & Budgets
    // -------------------------------------------------------------
    async getSummaryKPIs() {
        const res = await fetch('/api/analytics/summary');
        const data = await res.json();
        if (!data.success) throw new Error('Failed to load KPIs');
        return data.data;
    },

    async getCategoryAnalytics(params = {}) {
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`/api/analytics/categories?${query}`);
        const data = await res.json();
        if (!data.success) throw new Error('Failed to load category analytics');
        return data.data;
    },

    async getTrends() {
        const res = await fetch('/api/analytics/trends');
        const data = await res.json();
        if (!data.success) throw new Error('Failed to load trends');
        return data.data;
    },

    async getPaymentAnalytics() {
        const res = await fetch('/api/analytics/payment-methods');
        const data = await res.json();
        if (!data.success) throw new Error('Failed to load payment analytics');
        return data.data;
    },

    async updateBudget(amount) {
        const res = await fetch('/api/budget', {
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
