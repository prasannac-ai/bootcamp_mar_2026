from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

from ingestion import Event, KafkaEventProducer

app = FastAPI()
app_v1 = APIRouter(prefix="/api/v1",tags=["v1"])

class SensorData(BaseModel):
    sensor_id: str
    temperature: float
 

@app_v1.post("/sensor-data")
async def create_sensor_data(sensor_data: SensorData):
 
    return {"message": "sensor data ingested"}

app.include_router(app_v1)