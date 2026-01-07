// Simple API Helper for Cold Chain Monitor

async function fetchLatestData() {
    try {
        const response = await fetch('/api/sensors/latest/');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        return null;
    }
}

async function fetchAllData() {
    try {
        const response = await fetch('/api/sensors/all/');
        if (!response.ok) { throw new Error('Network response was not ok'); }
        return await response.json();
    } catch (error) {
        console.error('Error fetching all data:', error);
        return [];
    }
}

function updateElementText(id, text) {
    const el = document.getElementById(id);
    if (el) el.innerText = text;
}
