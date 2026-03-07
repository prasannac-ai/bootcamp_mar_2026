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
    event = Event(sensor_id=sensor_data.sensor_id, temperature=sensor_data.temperature)
    producer = KafkaEventProducer()
    await producer.publish_events(event)
    return {"message": "sensor data ingested"}

app.include_router(app_v1)