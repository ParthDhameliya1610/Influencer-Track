
const COLORS = {
    primary: '#4f46e5',
    success: '#10b981',
    warning: '#f59e0b',
    danger: '#ef4444',
    info: '#06b6d4',
    purple: '#8b5cf6',
    palette: [
        '#4f46e5', '#10b981', '#f59e0b', '#ef4444',
        '#06b6d4', '#8b5cf6', '#ec4899', '#14b8a6'
    ]
};

document.addEventListener('DOMContentLoaded', function () {
    loadCampaignBudgetChart();
    loadCategoryDistributionChart();
    loadEngagementByCategoryChart();
    loadTopInfluencersChart();
    loadRegistrationTrendChart();
    loadPlatformPerformanceChart();
    loadCollaborationStatusChart();
});


function loadCampaignBudgetChart() {
    fetch('/api/chart/campaign_budget')
        .then(r => r.json())
        .then(data => {
            const canvas = document.getElementById('campaignBudgetChart');
            if (!canvas || !data.labels.length) return;
            const ctx = canvas.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            gradient.addColorStop(0, COLORS.primary);
            gradient.addColorStop(1, '#a5b4fc');

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Budget ($)',
                        data: data.values,
                        backgroundColor: gradient,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { callbacks: { label: c => 'Budget: ' + formatCurrency(c.parsed.y) } }
                    },
                    scales: { y: { beginAtZero: true, ticks: { callback: v => '$' + v.toLocaleString() } } }
                }
            });
        });
}


function loadCategoryDistributionChart() {
    fetch('/api/chart/category_distribution')
        .then(r => r.json())
        .then(data => {
            const canvas = document.getElementById('categoryDistributionChart');
            if (!canvas || !data.labels.length) return;
            new Chart(canvas.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: COLORS.palette,
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'right', labels: { boxWidth: 12, font: { size: 11 } } } },
                    cutout: '60%'
                }
            });
        });
}


function loadEngagementByCategoryChart() {
    fetch('/api/chart/engagement_by_category')
        .then(r => r.json())
        .then(data => {
            const canvas = document.getElementById('engagementByCategoryChart');
            if (!canvas || !data.labels.length) return;
            new Chart(canvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Avg Engagement %',
                        data: data.values,
                        backgroundColor: COLORS.success,
                        borderRadius: 6
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { x: { beginAtZero: true, ticks: { callback: v => v + '%' } } }
                }
            });
        });
}


function loadTopInfluencersChart() {
    fetch('/api/chart/top_influencers')
        .then(r => r.json())
        .then(data => {
            const canvas = document.getElementById('topInfluencersChart');
            if (!canvas || !data.labels.length) return;
            new Chart(canvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [
                        {
                            label: 'Followers',
                            data: data.followers,
                            backgroundColor: COLORS.purple,
                            borderRadius: 6,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Engagement %',
                            data: data.engagement,
                            backgroundColor: COLORS.warning,
                            borderRadius: 6,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'top', labels: { boxWidth: 12 } } },
                    scales: {
                        y: { type: 'linear', position: 'left', beginAtZero: true, ticks: { callback: v => (v / 1000) + 'K' } },
                        y1: { type: 'linear', position: 'right', beginAtZero: true, grid: { drawOnChartArea: false }, ticks: { callback: v => v + '%' } }
                    }
                }
            });
        });
}


function loadRegistrationTrendChart() {
    fetch('/api/chart/registration_trend')
        .then(r => r.json())
        .then(data => {
            const canvas = document.getElementById('registrationTrendChart');
            if (!canvas || !data.labels.length) return;
            const ctx = canvas.getContext('2d');
            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
            gradient.addColorStop(0, 'rgba(6, 182, 212, 0.4)');
            gradient.addColorStop(1, 'rgba(6, 182, 212, 0.05)');

            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'New Influencers',
                        data: data.values,
                        borderColor: COLORS.info,
                        backgroundColor: gradient,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: COLORS.info,
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
                }
            });
        });
}


function loadPlatformPerformanceChart() {
    fetch('/api/chart/platform_performance')
        .then(r => r.json())
        .then(data => {
            const canvas = document.getElementById('platformPerformanceChart');
            if (!canvas) return;
            if (!data.labels.length) {
                canvas.parentElement.innerHTML = '<p class="text-muted text-center py-5">No platform data yet.</p>';
                return;
            }
            new Chart(canvas.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [
                        { label: 'Reach', data: data.reach, backgroundColor: COLORS.primary, borderRadius: 6 },
                        { label: 'Engagement', data: data.engagement, backgroundColor: COLORS.success, borderRadius: 6 }
                    ]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'top' } },
                    scales: { y: { beginAtZero: true } }
                }
            });
        });
}


function loadCollaborationStatusChart() {
    fetch('/api/chart/collaboration_status')
        .then(r => r.json())
        .then(data => {
            const canvas = document.getElementById('collaborationStatusChart');
            if (!canvas) return;
            if (!data.labels.length) {
                canvas.parentElement.innerHTML = '<p class="text-muted text-center py-5">No collaborations yet.</p>';
                return;
            }
            new Chart(canvas.getContext('2d'), {
                type: 'polarArea',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: [
                            'rgba(245, 158, 11, 0.7)',
                            'rgba(79, 70, 229, 0.7)',
                            'rgba(16, 185, 129, 0.7)',
                            'rgba(239, 68, 68, 0.7)',
                            'rgba(6, 182, 212, 0.7)'
                        ],
                        borderColor: '#fff',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false,
                    plugins: { legend: { position: 'right', labels: { boxWidth: 12, font: { size: 11 } } } }
                }
            });
        });
}