/**
 * Main Application Controller
 * Handles user interactions, state management, modal controllers, and rendering.
 */

const App = {
    // Current application state
    state: {
        page: 1,
        limit: 8,
        totalExpenses: 0,
        totalPages: 1,
        search: '',
        category: 'all',
        paymentMethod: 'all',
        sortBy: 'date',
        order: 'DESC',
        editingExpenseId: null,
        deleteTargetId: null,
        categories: [],
        paymentMethods: []
    },

    // Initialize application on DOM ready
    async init() {
        this.bindEvents();
        await this.loadInitialMetadata();
        await this.refreshAllData();
    },

    // Bind event listeners
    bindEvents() {
        // Search input with debounce
        let searchTimeout;
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.state.search = e.target.value;
                    this.state.page = 1;
                    this.loadExpenses();
                }, 300);
            });
        }

        // Category filter
        const categoryFilter = document.getElementById('categoryFilter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', (e) => {
                this.state.category = e.target.value;
                this.state.page = 1;
                this.loadExpenses();
            });
        }

        // Payment method filter
        const paymentFilter = document.getElementById('paymentFilter');
        if (paymentFilter) {
            paymentFilter.addEventListener('change', (e) => {
                this.state.paymentMethod = e.target.value;
                this.state.page = 1;
                this.loadExpenses();
            });
        }

        // Sort filter
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                const [sortBy, order] = e.target.value.split(':');
                this.state.sortBy = sortBy;
                this.state.order = order;
                this.loadExpenses();
            });
        }

        // Pagination buttons
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (this.state.page > 1) {
                    this.state.page--;
                    this.loadExpenses();
                }
            });
        }
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                if (this.state.page < this.state.totalPages) {
                    this.state.page++;
                    this.loadExpenses();
                }
            });
        }

        // Trend toggle buttons
        const dailyTrendBtn = document.getElementById('dailyTrendBtn');
        const monthlyTrendBtn = document.getElementById('monthlyTrendBtn');
        if (dailyTrendBtn && monthlyTrendBtn) {
            dailyTrendBtn.addEventListener('click', () => {
                dailyTrendBtn.className = "px-3 py-1.5 text-xs font-semibold rounded-md bg-indigo-600 text-white transition";
                monthlyTrendBtn.className = "px-3 py-1.5 text-xs font-medium rounded-md bg-slate-800 text-slate-400 hover:text-slate-200 transition";
                ChartsManager.renderTrendChart(null, 'daily');
            });
            monthlyTrendBtn.addEventListener('click', () => {
                monthlyTrendBtn.className = "px-3 py-1.5 text-xs font-semibold rounded-md bg-indigo-600 text-white transition";
                dailyTrendBtn.className = "px-3 py-1.5 text-xs font-medium rounded-md bg-slate-800 text-slate-400 hover:text-slate-200 transition";
                ChartsManager.renderTrendChart(null, 'monthly');
            });
        }

        // Expense Form submission
        const expenseForm = document.getElementById('expenseForm');
        if (expenseForm) {
            expenseForm.addEventListener('submit', (e) => this.handleExpenseSubmit(e));
        }

        // Budget Form submission
        const budgetForm = document.getElementById('budgetForm');
        if (budgetForm) {
            budgetForm.addEventListener('submit', (e) => this.handleBudgetSubmit(e));
        }

        // Confirm Delete button
        const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
        if (confirmDeleteBtn) {
            confirmDeleteBtn.addEventListener('click', () => this.handleConfirmDelete());
        }

        // Seed data button
        const seedBtn = document.getElementById('seedDemoBtn');
        if (seedBtn) {
            seedBtn.addEventListener('click', async () => {
                try {
                    await API.seedDemoData();
                    this.showToast('Sample demo expenses loaded successfully!', 'success');
                    await this.refreshAllData();
                } catch (err) {
                    this.showToast(err.message, 'error');
                }
            });
        }

        // Clear expenses button
        const clearBtn = document.getElementById('clearAllBtn');
        if (clearBtn) {
            clearBtn.addEventListener('click', async () => {
                if (confirm('Are you sure you want to delete ALL expense records? This cannot be undone.')) {
                    try {
                        await API.clearExpenses();
                        this.showToast('All expense records cleared', 'info');
                        await this.refreshAllData();
                    } catch (err) {
                        this.showToast(err.message, 'error');
                    }
                }
            });
        }
    },

    // Load static category and payment method definitions
    async loadInitialMetadata() {
        try {
            const [categories, paymentMethods] = await Promise.all([
                API.getCategories(),
                API.getPaymentMethods()
            ]);
            this.state.categories = categories;
            this.state.paymentMethods = paymentMethods;

            // Populate category select dropdowns
            const catFilter = document.getElementById('categoryFilter');
            const catSelect = document.getElementById('expenseCategory');
            if (catFilter) {
                catFilter.innerHTML = '<option value="all">All Categories</option>' +
                    categories.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
            }
            if (catSelect) {
                catSelect.innerHTML = categories.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
            }

            // Populate payment method dropdowns
            const payFilter = document.getElementById('paymentFilter');
            const paySelect = document.getElementById('expensePaymentMethod');
            if (payFilter) {
                payFilter.innerHTML = '<option value="all">All Payment Methods</option>' +
                    paymentMethods.map(m => `<option value="${m}">${m}</option>`).join('');
            }
            if (paySelect) {
                paySelect.innerHTML = paymentMethods.map(m => `<option value="${m}">${m}</option>`).join('');
            }

            // Set default date to today in expense form
            const dateInput = document.getElementById('expenseDate');
            if (dateInput) {
                dateInput.value = new Date().toISOString().split('T')[0];
            }
        } catch (err) {
            console.error("Failed to load metadata:", err);
        }
    },

    // Refresh all page metrics, analytics, and table data
    async refreshAllData() {
        await Promise.all([
            this.loadKPIs(),
            this.loadAnalyticsCharts(),
            this.loadExpenses()
        ]);
    },

    // Fetch and render KPI metric cards
    async loadKPIs() {
        try {
            const kpis = await API.getSummaryKPIs();

            // Total spent
            document.getElementById('kpiTotalSpent').textContent = `$${kpis.total_spent.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
            document.getElementById('kpiTotalCount').textContent = `${kpis.total_transactions} transactions`;

            // Monthly spent
            document.getElementById('kpiMonthlySpent').textContent = `$${kpis.monthly_spent.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
            document.getElementById('kpiDailyAvg').textContent = `Avg ~$${kpis.daily_avg.toFixed(2)}/day`;

            // Budget Info
            const b = kpis.budget;
            document.getElementById('kpiBudgetSpent').textContent = `$${b.spent.toFixed(2)}`;
            document.getElementById('kpiBudgetLimit').textContent = `$${b.limit.toFixed(2)}`;
            document.getElementById('kpiBudgetRemaining').textContent = `$${b.remaining.toFixed(2)} remaining`;

            const bar = document.getElementById('kpiBudgetBar');
            bar.style.width = `${Math.min(b.percentage, 100)}%`;

            // Status Badge
            const badge = document.getElementById('kpiBudgetBadge');
            badge.textContent = `${b.status} (${b.percentage}%)`;
            if (b.status === 'Healthy') {
                badge.className = 'px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
                bar.className = 'h-full rounded-full transition-all duration-500 bg-emerald-500';
            } else if (b.status === 'Near Limit') {
                badge.className = 'px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20';
                bar.className = 'h-full rounded-full transition-all duration-500 bg-amber-500';
            } else {
                badge.className = 'px-2 py-0.5 text-xs font-semibold rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20';
                bar.className = 'h-full rounded-full transition-all duration-500 bg-rose-500';
            }

            // Highest Expense
            if (kpis.highest_expense) {
                document.getElementById('kpiHighestTitle').textContent = kpis.highest_expense.title;
                document.getElementById('kpiHighestAmount').textContent = `$${kpis.highest_expense.amount.toFixed(2)}`;
                document.getElementById('kpiHighestDate').textContent = `${kpis.highest_expense.category} • ${kpis.highest_expense.date}`;
            } else {
                document.getElementById('kpiHighestTitle').textContent = 'None yet';
                document.getElementById('kpiHighestAmount').textContent = '$0.00';
                document.getElementById('kpiHighestDate').textContent = 'No records';
            }
        } catch (err) {
            console.error('Failed to load KPIs:', err);
        }
    },

    // Fetch and render analytics charts & category lists
    async loadAnalyticsCharts() {
        try {
            const [catData, trendsData, paymentData] = await Promise.all([
                API.getCategoryAnalytics(),
                API.getTrends(),
                API.getPaymentAnalytics()
            ]);

            // Render Category Doughnut Chart
            ChartsManager.renderCategoryChart(catData);

            // Render Category Legend List
            const legendEl = document.getElementById('categoryLegendList');
            if (legendEl) {
                const cats = catData.categories || [];
                if (cats.length === 0) {
                    legendEl.innerHTML = '<div class="text-sm text-slate-500 text-center py-4">No category data available</div>';
                } else {
                    legendEl.innerHTML = cats.slice(0, 5).map(c => `
                        <div class="flex items-center justify-between py-1.5 border-b border-slate-800/60 last:border-0 text-xs">
                            <div class="flex items-center gap-2">
                                <span class="w-2.5 h-2.5 rounded-full flex-shrink-0" style="background-color: ${c.color}"></span>
                                <span class="text-slate-300 font-medium truncate max-w-[120px]">${c.name}</span>
                            </div>
                            <div class="text-right">
                                <span class="text-slate-200 font-semibold">$${c.amount.toFixed(2)}</span>
                                <span class="text-slate-500 ml-1.5 font-mono">${c.percentage}%</span>
                            </div>
                        </div>
                    `).join('');
                }
            }

            // Render Trend Chart
            ChartsManager.renderTrendChart(trendsData);

            // Render Payment Methods Progress
            const payEl = document.getElementById('paymentBreakdownList');
            if (payEl) {
                if (paymentData.length === 0) {
                    payEl.innerHTML = '<div class="text-sm text-slate-500 text-center py-4">No payment data available</div>';
                } else {
                    payEl.innerHTML = paymentData.map(p => `
                        <div class="space-y-1">
                            <div class="flex justify-between text-xs">
                                <span class="text-slate-300 font-medium">${p.method} <span class="text-slate-500">(${p.count})</span></span>
                                <span class="text-slate-200 font-semibold">$${p.total.toFixed(2)} <span class="text-slate-500 font-mono">(${p.percentage}%)</span></span>
                            </div>
                            <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div class="bg-indigo-500 h-1.5 rounded-full" style="width: ${p.percentage}%"></div>
                            </div>
                        </div>
                    `).join('');
                }
            }
        } catch (err) {
            console.error('Failed to load analytics charts:', err);
        }
    },

    // Fetch and render paginated, filtered expenses
    async loadExpenses() {
        const offset = (this.state.page - 1) * this.state.limit;
        const params = {
            search: this.state.search,
            category: this.state.category,
            payment_method: this.state.paymentMethod,
            sort_by: this.state.sortBy,
            order: this.state.order,
            limit: this.state.limit,
            offset: offset
        };

        try {
            const data = await API.getExpenses(params);
            this.state.totalExpenses = data.total_count;
            this.state.totalPages = Math.ceil(data.total_count / this.state.limit) || 1;

            this.renderExpensesTable(data.expenses);
            this.renderPaginationControls();
        } catch (err) {
            console.error('Failed to load expenses:', err);
        }
    },

    // Render expense rows in HTML table
    renderExpensesTable(expenses) {
        const tbody = document.getElementById('expenseTableBody');
        const emptyState = document.getElementById('expenseEmptyState');
        const tableContainer = document.getElementById('expenseTableContainer');

        if (!tbody) return;

        if (expenses.length === 0) {
            tbody.innerHTML = '';
            if (emptyState) emptyState.classList.remove('hidden');
            if (tableContainer) tableContainer.classList.add('hidden');
            return;
        }

        if (emptyState) emptyState.classList.add('hidden');
        if (tableContainer) tableContainer.classList.remove('hidden');

        tbody.innerHTML = expenses.map(e => `
            <tr class="expense-row border-b border-slate-800/80 hover:bg-slate-800/40 transition">
                <td class="py-3 px-4">
                    <div class="font-medium text-slate-100">${this.escapeHTML(e.title)}</div>
                    ${e.notes ? `<div class="text-xs text-slate-400 truncate max-w-xs">${this.escapeHTML(e.notes)}</div>` : ''}
                </td>
                <td class="py-3 px-4">
                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold"
                          style="background-color: ${e.category_color}20; color: ${e.category_color}; border: 1px solid ${e.category_color}40;">
                        <span class="w-1.5 h-1.5 rounded-full" style="background-color: ${e.category_color}"></span>
                        ${e.category}
                    </span>
                </td>
                <td class="py-3 px-4 text-xs font-mono text-slate-300 whitespace-nowrap">
                    ${e.date}
                </td>
                <td class="py-3 px-4 text-xs text-slate-300">
                    <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60 font-medium">
                        ${e.payment_method}
                    </span>
                </td>
                <td class="py-3 px-4 text-right">
                    <span class="font-semibold text-slate-100 font-mono text-sm">$${parseFloat(e.amount).toFixed(2)}</span>
                </td>
                <td class="py-3 px-4 text-right whitespace-nowrap">
                    <button onclick="App.openEditModal(${e.id})"
                            class="p-1.5 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded-lg transition"
                            title="Edit Transaction">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                        </svg>
                    </button>
                    <button onclick="App.openDeleteModal(${e.id})"
                            class="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition ml-1"
                            title="Delete Transaction">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                        </svg>
                    </button>
                </td>
            </tr>
        `).join('');
    },

    // Update pagination buttons and text
    renderPaginationControls() {
        const info = document.getElementById('paginationInfo');
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');

        const start = this.state.totalExpenses === 0 ? 0 : (this.state.page - 1) * this.state.limit + 1;
        const end = Math.min(this.state.page * this.state.limit, this.state.totalExpenses);

        if (info) {
            info.textContent = `Showing ${start}-${end} of ${this.state.totalExpenses}`;
        }

        if (prevBtn) {
            prevBtn.disabled = this.state.page <= 1;
            prevBtn.classList.toggle('opacity-40', this.state.page <= 1);
            prevBtn.classList.toggle('cursor-not-allowed', this.state.page <= 1);
        }

        if (nextBtn) {
            nextBtn.disabled = this.state.page >= this.state.totalPages;
            nextBtn.classList.toggle('opacity-40', this.state.page >= this.state.totalPages);
            nextBtn.classList.toggle('cursor-not-allowed', this.state.page >= this.state.totalPages);
        }
    },

    // -------------------------------------------------------------
    // Modal Controllers & Actions
    // -------------------------------------------------------------
    openAddModal() {
        this.state.editingExpenseId = null;
        document.getElementById('modalTitle').textContent = 'Add New Expense';
        document.getElementById('modalSubmitBtn').textContent = 'Add Expense';
        document.getElementById('expenseForm').reset();
        document.getElementById('expenseDate').value = new Date().toISOString().split('T')[0];
        document.getElementById('expenseModal').classList.remove('hidden');
    },

    async openEditModal(id) {
        try {
            const expense = await API.getExpenseById(id);
            this.state.editingExpenseId = id;
            document.getElementById('modalTitle').textContent = 'Edit Expense';
            document.getElementById('modalSubmitBtn').textContent = 'Save Changes';

            document.getElementById('expenseTitle').value = expense.title;
            document.getElementById('expenseAmount').value = expense.amount;
            document.getElementById('expenseCategory').value = expense.category;
            document.getElementById('expenseDate').value = expense.date;
            document.getElementById('expensePaymentMethod').value = expense.payment_method;
            document.getElementById('expenseNotes').value = expense.notes || '';

            document.getElementById('expenseModal').classList.remove('hidden');
        } catch (err) {
            this.showToast(err.message, 'error');
        }
    },

    closeExpenseModal() {
        document.getElementById('expenseModal').classList.add('hidden');
        this.state.editingExpenseId = null;
    },

    async handleExpenseSubmit(e) {
        e.preventDefault();
        const payload = {
            title: document.getElementById('expenseTitle').value,
            amount: parseFloat(document.getElementById('expenseAmount').value),
            category: document.getElementById('expenseCategory').value,
            date: document.getElementById('expenseDate').value,
            payment_method: document.getElementById('expensePaymentMethod').value,
            notes: document.getElementById('expenseNotes').value
        };

        try {
            if (this.state.editingExpenseId) {
                await API.updateExpense(this.state.editingExpenseId, payload);
                this.showToast('Expense updated successfully!', 'success');
            } else {
                await API.createExpense(payload);
                this.showToast('New expense recorded!', 'success');
            }
            this.closeExpenseModal();
            await this.refreshAllData();
        } catch (err) {
            this.showToast(err.message, 'error');
        }
    },

    openDeleteModal(id) {
        this.state.deleteTargetId = id;
        document.getElementById('deleteModal').classList.remove('hidden');
    },

    closeDeleteModal() {
        this.state.deleteTargetId = null;
        document.getElementById('deleteModal').classList.add('hidden');
    },

    async handleConfirmDelete() {
        if (!this.state.deleteTargetId) return;
        try {
            await API.deleteExpense(this.state.deleteTargetId);
            this.showToast('Expense deleted successfully', 'info');
            this.closeDeleteModal();
            await this.refreshAllData();
        } catch (err) {
            this.showToast(err.message, 'error');
        }
    },

    openBudgetModal() {
        document.getElementById('budgetModal').classList.remove('hidden');
    },

    closeBudgetModal() {
        document.getElementById('budgetModal').classList.add('hidden');
    },

    async handleBudgetSubmit(e) {
        e.preventDefault();
        const amount = document.getElementById('budgetAmountInput').value;
        try {
            await API.updateBudget(amount);
            this.showToast('Monthly budget updated!', 'success');
            this.closeBudgetModal();
            await this.loadKPIs();
        } catch (err) {
            this.showToast(err.message, 'error');
        }
    },

    // -------------------------------------------------------------
    // Toast Notification System
    // -------------------------------------------------------------
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        let bg = 'bg-slate-800 text-slate-100 border border-slate-700';
        let icon = 'ℹ️';

        if (type === 'success') {
            bg = 'bg-emerald-950/90 text-emerald-200 border border-emerald-700/60';
            icon = '✓';
        } else if (type === 'error') {
            bg = 'bg-rose-950/90 text-rose-200 border border-rose-700/60';
            icon = '✕';
        } else if (type === 'info') {
            bg = 'bg-indigo-950/90 text-indigo-200 border border-indigo-700/60';
            icon = '✦';
        }

        toast.className = `toast ${bg}`;
        toast.innerHTML = `
            <span class="font-bold text-base">${icon}</span>
            <span class="flex-1">${message}</span>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
            setTimeout(() => toast.remove(), 300);
        }, 3200);
    },

    // Utility: XSS escape
    escapeHTML(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
};

window.App = App;

// Bootstrap application on window load
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
