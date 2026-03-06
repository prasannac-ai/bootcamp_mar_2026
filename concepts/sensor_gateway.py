from fastapi import FastAPI, APIRouter, HTTPException, status
from pydantic import BaseModel
import requests
import uuid

app = FastAPI()
app_v1 = APIRouter(prefix="/api/v1",tags=["v1"])

class SensorData(BaseModel):
    sensor_id: str
    temperature: float
 

@app_v1.post("/sensor-data")
def create_sensor_data(sensor_data: SensorData):
    if sensor_data.temperature > 30:
        irrigation_payload = {
            "irrigation_id": str(uuid.uuid4()),
            "irrigation_status": "start",
            "irrigation_duration": 10
        }
        irrigation_response = requests.post("http://irrigation:8000/api/v1/irrigation-data", json=irrigation_payload)
        print("Irrigation response status code: ", irrigation_response.status_code)
        if irrigation_response.status_code == 200:
            return irrigation_response.json()
        else:
            print("Failed to create irrigation data")
            return {"message": "Failed to create irrigation data"}
    else:
        return {"message": "Temperature is normal, no irrigation needed"}



app.include_router(app_v1)