import requests
import time
import random
from datetime import datetime
from typing import Dict

# Backend endpoint
BACKEND_URL = "https://bus-tracker-api-ylin.onrender.com"

# Demo buses and route points (interpolate between stops)
ROUTE_POINTS = [
    (40.7128, -74.0060),  # A
    (40.7133, -74.0065),  # Midway A-B
    (40.7138, -74.0070),  # B
    (40.7143, -74.0075),  # Midway B-C
    (40.7148, -74.0080),  # C
    (40.7133, -74.0065),  # Back midway
    (40.7128, -74.0060),  # A
]

def simulate_bus(bus_id: str):
    """Simulate one bus moving along route."""
    point_idx = 0
    while True:
        lat, lon = ROUTE_POINTS[point_idx % len(ROUTE_POINTS)]
        # Add noise for realism
        lat += random.uniform(-0.0005, 0.0005)
        lon += random.uniform(-0.0005, 0.0005)
        
        payload = {
            "bus_id": bus_id,
            "lat": lat,
            "lon": lon,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(BACKEND_URL, json=payload)
            if response.status_code == 200:
                eta = response.json().get("eta", "N/A")
                print(f"Bus {bus_id}: {lat:.4f}, {lon:.4f} | ETA: {eta} min")
            else:
                print(f"Error sending for {bus_id}: {response.status_code}")
        except Exception as e:
            print(f"Connection error for {bus_id}: {e}")
        
        time.sleep(5)  # Ping every 5s
        point_idx += 1

if __name__ == "__main__":
    # Simulate 2 buses
    import threading
    threads = []
    for i in range(1, 3):
        bus_id = f"bus{i}"
        t = threading.Thread(target=simulate_bus, args=(bus_id,))
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()

