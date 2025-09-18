from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime
from typing import Dict, List
from models import BusLocation, BusUpdate
from eta_engine import calculate_eta

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
buses: Dict[str, List[BusLocation]] = {}  # bus_id -> list of recent locations (keep last 5)
connected_clients: List[WebSocket] = []

@app.post("/location")
async def receive_location(location: BusLocation):
    """Receive GPS ping from bus/simulator."""
    bus_id = location.bus_id
    if bus_id not in buses:
        buses[bus_id] = []
    # Keep only last 5 for speed calc
    buses[bus_id].append(location)
    if len(buses[bus_id]) > 5:
        buses[bus_id].pop(0)
    
    # Calculate ETA
    eta_minutes, next_stop = calculate_eta(location, buses[bus_id])
    speed = buses[bus_id][-1].speed if buses[bus_id][-1].speed else 0
    status = "stopped" if speed < 5 else "moving"
    
    # Broadcast update
    update = BusUpdate(
        bus_id=bus_id,
        lat=location.lat,
        lon=location.lon,
        eta_minutes=eta_minutes,
        next_stop=next_stop,
        status=status
    )
    await broadcast_update(update)
    return {"status": "received", "eta": eta_minutes}

async def broadcast_update(update: BusUpdate):
    """Send update to all connected clients via WS."""
    if connected_clients:
        message = json.dumps(update.dict())
        disconnected = []
        for client in connected_clients:
            try:
                await client.send_text(message)
            except:
                disconnected.append(client)
        for client in disconnected:
            connected_clients.remove(client)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Optional: Handle client messages if needed
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

@app.get("/")
async def get_index():
    """Serve a simple HTML for testing (but use frontend/index.html for map)."""
    html = """
    <html><body><h1>Bus Tracker Backend</h1><p>Run simulator and open frontend/index.html</p></body></html>
    """
    return HTMLResponse(html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
