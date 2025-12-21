class DashboardBase {
    constructor(type) {
        this.type = type; // 'temp' ou 'hum'
        this.chart = null;
        this.currentPeriod = 'jour';
        this.baseUrls = {
            jour: '/chart-data-jour/',
            semaine: '/chart-data-semaine/',
            mois: '/chart-data-mois/',
            dateTemp: '/chart-data-date-temp/',
            dateHum: '/chart-data-date-hum/'
        };
    }

    init() {
        this.initElements();
        this.initEventListeners();
        this.loadInitialData();
    }

    initElements() {
        const prefix = this.type === 'temp' ? 'temp' : 'hum';

        this.elements = {
            periodDisplay: document.getElementById(`periode-${prefix}`),
            chartCanvas: document.getElementById(`graphique-${prefix}`),
            loadingOverlay: document.getElementById('loading-overlay'),
            dateInput: document.getElementById(`date-input-${prefix}`),
            periodButtons: document.querySelectorAll('.period-btn'),
            stats: {
                current: document.getElementById('current-value'),
                avg: document.getElementById('avg-value'),
                min: document.getElementById('min-value'),
                max: document.getElementById('max-value')
            }
        };

        // Set default date to today
        if (this.elements.dateInput) {
            this.elements.dateInput.value = new Date().toISOString().split('T')[0];
        }
    }

    initEventListeners() {
        const dateBtnId = this.type === 'temp' ? 'btn-date-temp' : 'btn-date-hum';

        this.elements.periodButtons.forEach(btn => {
            btn.addEventListener('click', (e) => this.handlePeriodChange(e));
        });

        document.getElementById(dateBtnId).addEventListener('click', () => this.handleDateSelect());

        if (this.elements.dateInput) {
            this.elements.dateInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.handleDateSelect();
            });
        }
    }

    handlePeriodChange(event) {
        const period = event.currentTarget.dataset.period;
        this.setActivePeriod(period);

        switch(period) {
            case 'jour':
                this.updatePeriodDisplay('jour');
                this.loadData(this.baseUrls.jour);
                break;
            case 'semaine':
                this.updatePeriodDisplay('semaine');
                this.loadData(this.baseUrls.semaine);
                break;
            case 'mois':
                this.updatePeriodDisplay('mois');
                this.loadData(this.baseUrls.mois);
                break;
        }
    }

    handleDateSelect() {
        const date = this.elements.dateInput.value;
        if (!date) {
            this.showNotification('Veuillez sélectionner une date.', 'warning');
            return;
        }
        this.updatePeriodDisplay('date', date);

        const url = this.type === 'temp'
            ? `${this.baseUrls.dateTemp}?date=${date}`
            : `${this.baseUrls.dateHum}?date=${date}`;

        this.loadData(url);
    }

    setActivePeriod(period) {
        this.currentPeriod = period;
        this.elements.periodButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.period === period);
        });
    }

    updatePeriodDisplay(type, dateString = null) {
        const now = new Date();
        let text = '';

        switch(type) {
            case 'jour':
                text = `Aujourd'hui - ${now.toLocaleDateString('fr-FR', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                })}`;
                break;
            case 'semaine':
                const weekStart = new Date(now);
                weekStart.setDate(now.getDate() - 6);
                text = `Du ${weekStart.toLocaleDateString('fr-FR')} au ${now.toLocaleDateString('fr-FR')}`;
                break;
            case 'mois':
                const monthStart = new Date(now);
                monthStart.setDate(now.getDate() - 29);
                text = `Du ${monthStart.toLocaleDateString('fr-FR')} au ${now.toLocaleDateString('fr-FR')}`;
                break;
            case 'date':
                const date = new Date(dateString);
                text = `Date spécifique - ${date.toLocaleDateString('fr-FR', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                })}`;
                break;
            default:
                text = this.type === 'temp'
                    ? 'Dernières mesures de température'
                    : 'Dernières mesures d\'humidité';
        }

        this.elements.periodDisplay.textContent = text;
    }

    async loadData(url) {
        this.showLoading(true);

        try {
            // CORRECTION CRITIQUE : Utiliser l'URL complète pour PythonAnywhere
            const fullUrl = window.location.origin + url;
            console.log(`Chargement ${this.type} depuis:`, fullUrl);

            const response = await fetch(fullUrl);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();
            console.log(`Données ${this.type} reçues:`, data);

            // CORRECTION CRITIQUE : Adapter aux clés existantes de votre API
            // Votre API retourne 'temp' et 'hum', pas 'temperature' et 'humidity'
            const chartData = this.prepareChartData(data);

            if (chartData.values.length === 0) {
                this.showNotification(`Aucune donnée de ${this.type === 'temp' ? 'température' : 'humidité'} disponible`, 'warning');
            } else {
                this.renderChart(chartData);
                this.updateStats(chartData);
            }
        } catch (error) {
            console.error(`Erreur lors du chargement des données ${this.type}:`, error);
            this.showNotification('Erreur lors du chargement des données: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    prepareChartData(data) {
        // CORRECTION : Votre API retourne 'temp' et 'hum'
        const values = this.type === 'temp' ? (data.temp || []) : (data.hum || []);
        const times = data.temps || [];

        return {
            values: values,
            times: times,
            rawData: data
        };
    }

    renderChart(chartData) {
        const ctx = this.elements.chartCanvas.getContext('2d');

        // Destroy existing chart
        if (this.chart) {
            this.chart.destroy();
        }

        // Prepare gradient for fill
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        if (this.type === 'temp') {
            gradient.addColorStop(0, 'rgba(0, 123, 255, 0.3)');
            gradient.addColorStop(1, 'rgba(0, 123, 255, 0.05)');
        } else {
            gradient.addColorStop(0, 'rgba(40, 167, 69, 0.3)');
            gradient.addColorStop(1, 'rgba(40, 167, 69, 0.05)');
        }

        const chartConfig = {
            type: 'line',
            data: {
                labels: chartData.times.map(d => new Date(d)),
                datasets: [{
                    label: this.type === 'temp' ? 'Température (°C)' : 'Humidité (%)',
                    data: chartData.values,
                    borderColor: this.type === 'temp' ? '#007bff' : '#28a745',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    pointRadius: 4,
                    pointBackgroundColor: this.type === 'temp' ? '#007bff' : '#28a745',
                    pointBorderColor: 'white',
                    pointBorderWidth: 2,
                    pointHoverRadius: 8,
                    fill: true,
                    tension: 0.2
                }]
            },
            options: this.getChartOptions()
        };

        this.chart = new Chart(ctx, chartConfig);
    }

    getChartOptions() {
        const unit = this.type === 'temp' ? '°C' : '%';
        const label = this.type === 'temp' ? 'Température' : 'Humidité';

        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: (context) => `${label}: ${context.parsed.y}${unit}`
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: this.getTimeUnit(),
                        tooltipFormat: 'DD/MM/YYYY HH:mm',
                        displayFormats: {
                            hour: 'HH:mm',
                            day: 'DD/MM',
                            week: 'DD/MM',
                            month: 'MM/YYYY'
                        }
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                y: {
                    ticks: {
                        beginAtZero: false,
                        callback: value => value + unit,
                        maxTicksLimit: 8
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                }
            },
            hover: {
                mode: 'nearest',
                intersect: false
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        };
    }

    getTimeUnit() {
        switch(this.currentPeriod) {
            case 'jour': return 'hour';
            case 'semaine': return 'day';
            case 'mois': return 'day';
            default: return 'hour';
        }
    }

    updateStats(chartData) {
        const values = chartData.values || [];

        if (values.length === 0) {
            const unit = this.type === 'temp' ? '°C' : '%';
            this.elements.stats.current.textContent = `--${unit}`;
            this.elements.stats.avg.textContent = `--${unit}`;
            this.elements.stats.min.textContent = `--${unit}`;
            this.elements.stats.max.textContent = `--${unit}`;
            return;
        }

        const current = values[values.length - 1];
        const avg = values.reduce((a, b) => a + b, 0) / values.length;
        const min = Math.min(...values);
        const max = Math.max(...values);

        const unit = this.type === 'temp' ? '°C' : '%';
        this.elements.stats.current.textContent = `${current.toFixed(1)}${unit}`;
        this.elements.stats.avg.textContent = `${avg.toFixed(1)}${unit}`;
        this.elements.stats.min.textContent = `${min.toFixed(1)}${unit}`;
        this.elements.stats.max.textContent = `${max.toFixed(1)}${unit}`;

        // Color coding for temperature
        if (this.type === 'temp') {
            this.colorCodeTemperature(current, 'current');
        }
    }

    colorCodeTemperature(temp, element) {
        let color;
        if (temp < 10) {
            color = '#007bff'; // Cold - blue
        } else if (temp < 25) {
            color = '#28a745'; // Comfortable - green
        } else if (temp < 30) {
            color = '#ffc107'; // Warm - yellow
        } else {
            color = '#dc3545'; // Hot - red
        }
        this.elements.stats[element].style.color = color;
    }

    loadInitialData() {
        this.updatePeriodDisplay('jour');
        this.loadData(this.baseUrls.jour);
    }

    showLoading(show) {
        this.elements.loadingOverlay.style.display = show ? 'flex' : 'none';
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        // Set background color based on type
        const bgColor = type === 'error' ? '#dc3545' :
                       type === 'warning' ? '#ffc107' :
                       (this.type === 'temp' ? '#007bff' : '#28a745');

        notification.style.backgroundColor = bgColor;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.padding = '1rem 1.5rem';
        notification.style.borderRadius = '8px';
        notification.style.color = 'white';
        notification.style.fontWeight = '600';
        notification.style.zIndex = '1000';
        notification.style.animation = 'slideIn 0.3s ease';

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Classes spécifiques
class TemperatureDashboard extends DashboardBase {
    constructor() {
        super('temp');
        this.init();
    }
}

class HumidityDashboard extends DashboardBase {
    constructor() {
        super('hum');
        this.init();
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    // Vérifier sur quelle page nous sommes
    if (document.getElementById('graphique-temp')) {
        new TemperatureDashboard();
    }
    if (document.getElementById('graphique-hum')) {
        new HumidityDashboard();
    }
});