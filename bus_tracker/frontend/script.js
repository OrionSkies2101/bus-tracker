const map = L.map('map').setView([40.7135, -74.007], 15);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const buses = {};  // bus_id -> marker
const ws = new WebSocket('ws://localhost:8000/ws');
let pollInterval;

ws.onmessage = function(event) {
    const update = JSON.parse(event.data);
    updateBus(update);
};

ws.onclose = function() {
    console.log('WS closed, starting poll fallback');
    startPolling();
};

function updateBus(update) {
    const { bus_id, lat, lon, eta_minutes, next_stop, status } = update;
    if (!buses[bus_id]) {
        buses[bus_id] = L.marker([lat, lon]).addTo(map)
            .bindPopup(`Bus ${bus_id}<br>ETA: ${eta_minutes} min<br>Next: ${next_stop}<br>Status: ${status}`);
    } else {
        buses[bus_id].setLatLng([lat, lon]);
    }
    buses[bus_id].openPopup();
    updateInfoPanel(update);
}

function updateInfoPanel(update) {
    const details = document.getElementById('bus-details');
    details.innerHTML = `
        <p><strong>Bus ${update.bus_id}</strong></p>
        <p>ETA: ${update.eta_minutes} min</p>
        <p>Next Stop: ${update.next_stop}</p>
        <p>Status: ${update.status}</p>
    `;
}

function startPolling() {
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch('http://localhost:8000/buses');  // Add endpoint if needed, or simulate
            // For demo, assume WS handles; extend with /buses GET if offline
            console.log('Polling...');
        } catch (e) {
            console.error('Poll failed:', e);
        }
    }, 30000);  // 30s
}

// Initial stops markers (optional)
const stops = {
    'A': [40.7128, -74.0060],
    'B': [40.7138, -74.0070],
    'C': [40.7148, -74.0080]
};
Object.entries(stops).forEach(([name, coords]) => {
    L.marker(coords).addTo(map).bindPopup(`Stop ${name}`);
});
