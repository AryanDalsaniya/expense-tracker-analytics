/**
 * Chart Visualization Module
 * Powered by Chart.js with custom dark-mode styling and gradients.
 */

const ChartsManager = {
    categoryChartInstance: null,
    trendChartInstance: null,
    activeTrendMode: 'daily', // 'daily' or 'monthly'
    trendDataCache: null,

    // Initialize or refresh Category Doughnut Chart
    renderCategoryChart(categoriesData) {
        const ctx = document.getElementById('categoryChartCanvas');
        if (!ctx) return;

        if (this.categoryChartInstance) {
            this.categoryChartInstance.destroy();
        }

        const categories = categoriesData.categories || [];
        if (categories.length === 0) {
            // Render placeholder or empty state
            return;
        }

        const labels = categories.map(c => c.name);
        const data = categories.map(c => c.amount);
        const colors = categories.map(c => c.color || '#6366f1');

        this.categoryChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderColor: '#111827',
                    borderWidth: 2,
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: {
                        display: false // We render a custom sleek legend in HTML
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        titleColor: '#f8fafc',
                        bodyColor: '#cbd5e1',
                        padding: 12,
                        cornerRadius: 8,
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                const val = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                                return ` $${val.toFixed(2)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    },

    // Initialize or refresh Trends Chart (Daily or Monthly)
    renderTrendChart(trendsData, mode = null) {
        const ctx = document.getElementById('trendChartCanvas');
        if (!ctx) return;

        if (trendsData) {
            this.trendDataCache = trendsData;
        }
        if (mode) {
            this.activeTrendMode = mode;
        }

        const dataToRender = this.trendDataCache;
        if (!dataToRender) return;

        if (this.trendChartInstance) {
            this.trendChartInstance.destroy();
        }

        let labels = [];
        let values = [];
        let chartLabel = '';

        if (this.activeTrendMode === 'daily') {
            chartLabel = 'Daily Spend ($)';
            const daily = dataToRender.daily || [];
            labels = daily.map(d => d.label);
            values = daily.map(d => d.amount);
        } else {
            chartLabel = 'Monthly Spend ($)';
            const monthly = dataToRender.monthly || [];
            labels = monthly.map(m => m.label);
            values = monthly.map(m => m.total);
        }

        // Create gradient fill
        const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(99, 102, 241, 0.45)');
        gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

        this.trendChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: chartLabel,
                    data: values,
                    borderColor: '#6366f1',
                    borderWidth: 2.5,
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.35,
                    pointBackgroundColor: '#818cf8',
                    pointBorderColor: '#1e1b4b',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.04)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.04)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 },
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        titleColor: '#f8fafc',
                        bodyColor: '#cbd5e1',
                        padding: 12,
                        cornerRadius: 8,
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return ` Spent: $${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                }
            }
        });
    }
};

window.ChartsManager = ChartsManager;
