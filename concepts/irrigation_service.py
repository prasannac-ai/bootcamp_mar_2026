from fastapi import FastAPI, APIRouter, HTTPException, status
from pydantic import BaseModel
from ingestion import Event



class IrrigationData(BaseModel):
    irrigation_id: str
    irrigation_status: str
    irrigation_duration: int
    
class IrrigationService:
    def __init__(self):
        self.irrigation_data = []

    def create_irrigation_data(self, event: Event):
        if event.temperature > 30:
            print(f"Irrigation process initiated based on sensor {event.sensor_id} with temperature {event.temperature}", flush=True)
        else:
            print(f"Irrigation process not initiated based on sensor {event.sensor_id} with temperature {event.temperature}", flush=True)

