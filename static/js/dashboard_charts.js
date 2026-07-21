document.addEventListener("DOMContentLoaded", function () {
    const apiEndpoint = "/api/chart-data/";

    fetch(apiEndpoint)
        .then(response => response.json())
        .then(data => {
            renderIncomeVsExpenseChart(data.income_vs_expense);
            renderCategoryWiseChart(data.category_wise);
            renderMonthlyTrendChart(data.monthly_trends);
        })
        .catch(error => console.error("Error loading chart data:", error));
});

function renderIncomeVsExpenseChart(chartData) {
    const ctx = document.getElementById("incomeExpenseChart");
    if (!ctx) return;

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: chartData.labels,
            datasets: [{
                label: "Amount ($)",
                data: chartData.data,
                backgroundColor: ["rgba(16, 185, 129, 0.8)", "rgba(244, 63, 94, 0.8)"],
                borderColor: ["#10b981", "#f43f5e"],
                borderWidth: 2,
                borderRadius: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#94a3b8" }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: "#94a3b8" }
                }
            }
        }
    });
}

function renderCategoryWiseChart(chartData) {
    const ctx = document.getElementById("categoryChart");
    if (!ctx) return;

    if (!chartData.labels.length) {
        ctx.parentElement.innerHTML = "<div class='text-center py-5 text-muted'>No expense category data available yet.</div>";
        return;
    }

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: chartData.colors,
                borderWidth: 2,
                borderColor: "#0f172a",
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "right",
                    labels: { color: "#f8fafc", padding: 12 }
                }
            },
            cutout: "65%"
        }
    });
}

function renderMonthlyTrendChart(chartData) {
    const ctx = document.getElementById("trendChart");
    if (!ctx) return;

    new Chart(ctx, {
        type: "line",
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: "Income ($)",
                    data: chartData.income,
                    borderColor: "#10b981",
                    backgroundColor: "rgba(16, 185, 129, 0.1)",
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4
                },
                {
                    label: "Expenses ($)",
                    data: chartData.expenses,
                    borderColor: "#f43f5e",
                    backgroundColor: "rgba(244, 63, 94, 0.1)",
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "top",
                    labels: { color: "#f8fafc" }
                }
            },
            scales: {
                y: {
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#94a3b8" }
                },
                x: {
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#94a3b8" }
                }
            }
        }
    });
}
