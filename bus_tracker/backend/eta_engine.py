import math
from datetime import datetime, timedelta
from typing import Tuple, Optional
from models import BusLocation

# Hardcoded stops for demo (lat, lon, name)
STOPS = {
    'A': (40.7128, -74.0060),
    'B': (40.7138, -74.0070),
    'C': (40.7148, -74.0080)
}
ROUTE_ORDER = ['A', 'B', 'C']  # Loop: A->B->C->A

EARTH_RADIUS_KM = 6371  # For haversine

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two lat/lon points in km using Haversine formula."""
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM * c

def find_next_stop(bus_pos: Tuple[float, float], bus_id: str) -> Tuple[str, float]:
    """Determine next stop and distance to it based on current position and route."""
    # Simple: Find closest upcoming stop in route order. For demo, assume bus_id % 2 determines starting point.
    start_idx = int(bus_id[-1]) % len(ROUTE_ORDER)  # e.g., bus1 starts at A (0), bus2 at B (1)
    distances = {}
    for i in range(len(ROUTE_ORDER)):
        next_idx = (start_idx + i) % len(ROUTE_ORDER)
        stop_name = ROUTE_ORDER[next_idx]
        stop_lat, stop_lon = STOPS[stop_name]
        dist = haversine_distance(bus_pos[0], bus_pos[1], stop_lat, stop_lon)
        distances[stop_name] = dist
        if dist < 0.5:  # Close enough? It's next.
            return stop_name, dist
    # Otherwise, closest upcoming
    closest_stop = min(distances, key=distances.get)
    return closest_stop, distances[closest_stop]

def calculate_speed(recent_locations: list[BusLocation]) -> float:
    """Calculate speed from last two locations (km/h). Fallback to avg 10 km/h if <1 min data or stopped."""
    if len(recent_locations) < 2:
        return 10.0
    loc1, loc2 = recent_locations[-2], recent_locations[-1]
    time_diff_hours = (loc2.timestamp - loc1.timestamp).total_seconds() / 3600
    if time_diff_hours < 1/60:  # Less than 1 min
        return 10.0
    dist_km = haversine_distance(loc1.lat, loc1.lon, loc2.lat, loc2.lon)
    speed = dist_km / time_diff_hours if time_diff_hours > 0 else 0
    return max(speed, 5.0) if speed > 0 else 10.0  # Min 5 km/h moving, fallback 10 if stopped

def calculate_eta(bus_location: BusLocation, recent_locations: list[BusLocation]) -> Tuple[float, str]:
    """Calculate ETA in minutes to next stop."""
    speed_kmh = calculate_speed(recent_locations)
    next_stop, distance_km = find_next_stop((bus_location.lat, bus_location.lon), bus_location.bus_id)
    if distance_km == 0:
        return 0, next_stop
    time_hours = distance_km / speed_kmh
    eta_minutes = max(1, round(time_hours * 60))  # Min 1 min
    status = "stopped" if speed_kmh < 5 else "moving"
    return eta_minutes, next_stop
