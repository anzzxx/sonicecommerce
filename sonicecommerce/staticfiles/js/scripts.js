// Bar Chart
const ctxBar = document.getElementById('barChart').getContext('2d');
const barChart = new Chart(ctxBar, {
    type: 'bar',
    data: {
        labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        datasets: [{
            label: 'Sales',
            data: [1200, 1900, 3000, 5000, 2300, 3500, 4200, 5300, 6100, 7000, 8000, 9500],
            backgroundColor: '#3e64ff'
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

// Pie Chart for Visitors
const ctxPieVisitors = document.getElementById('pieChartVisitors').getContext('2d');
const pieChartVisitors = new Chart(ctxPieVisitors, {
    type: 'pie',
    data: {
        labels: ['Returning Visitors', 'New Visitors'],
        datasets: [{
            label: 'Visitors',
            data: [60, 40],
            backgroundColor: ['#4caf50', '#ff9800']
        }]
    }
});

// Pie Chart for Sales Breakdown
const ctxPieSales = document.getElementById('pieChartSales').getContext('2d');
const pieChartSales = new Chart(ctxPieSales, {
    type: 'pie',
    data: {
        labels: ['Net Profit', 'Paypal Fee', 'Shipping', 'Tax', 'Cost'],
        datasets: [{
            label: 'Sales Breakdown',
            data: [502520, 62180, 220930, 82140, 608180],
            backgroundColor: ['#4caf50', '#ff9800', '#f44336', '#2196f3', '#9c27b0']
        }]
    }
});
