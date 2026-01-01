document.addEventListener('DOMContentLoaded', function() {
    function updateDashboard() {
        fetch('/latest/')
            .then(response => response.json())
            .then(data => {
                if (data) {
                    // Update Temperature
                    document.getElementById('temp-value').textContent = data.temp + ' °C';
                    
                    // Update Humidity
                    document.getElementById('hum-value').textContent = data.hum + ' %';
                    
                    // Calculate "Time Ago"
                    if (data.dt) {
                        const date = new Date(data.dt);
                        const now = new Date();
                        const diffMs = now - date;
                        const diffMins = Math.floor(diffMs / 60000);
                        
                        let timeText = `il y a ${diffMins} min`;
                        if (diffMins < 1) timeText = "à l'instant";
                        else if (diffMins > 60) {
                             const hours = Math.floor(diffMins / 60);
                             const minutes = diffMins % 60;
                             timeText = `il y a ${hours}h ${minutes}min`;
                        }
                        
                        document.getElementById('temp-time').textContent = timeText;
                        document.getElementById('hum-time').textContent = timeText;
                    }
                }
            })
            .catch(error => console.error('Error fetching data:', error));
    }

    // Initial call
    updateDashboard();

    // Update every 5 seconds
    setInterval(updateDashboard, 5000);
});
