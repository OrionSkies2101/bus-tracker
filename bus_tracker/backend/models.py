from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BusLocation(BaseModel):
    bus_id: str
    lat: float
    lon: float
    timestamp: datetime
    speed: Optional[float] = None  # km/h

class BusUpdate(BaseModel):
    bus_id: str
    lat: float
    lon: float
    eta_minutes: Optional[float] = None
    next_stop: Optional[str] = None
    status: str  # e.g., "moving", "stopped"
