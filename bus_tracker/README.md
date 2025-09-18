# Bus Tracker Demo

## Setup
1. Install Python deps: `pip install -r backend/requirements.txt`
2. Start backend: `cd backend && uvicorn main:app --reload`
3. Run simulator: `cd simulator && python bus_simulator.py` (in new terminal)
4. Open frontend: `cd frontend && open index.html` (or in browser)

## Testing
- Simulator sends fake GPS every 5s.
- Backend calculates ETA and broadcasts via WS.
- Frontend shows map with moving buses; click for details.
- Disconnect WS? Falls back to polling.

## Scalability
- Add Redis/DB for prod storage.
- Deploy backend to Render: `git push render main`
- Frontend: Host static on GitHub Pages/Netlify.

## Customization
- Update STOPS/ROUTE in eta_engine.py for your town.
- Real GPS: Replace simulator with device API (e.g., phone GPS via MQTT).

Full system ready! Ping for tweaks.
