"""
Kafka Producer Utility
"""

import asyncio
import json

from pydantic import BaseModel
from aiokafka import AIOKafkaProducer



KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
TOPIC_NAME = "sensor.events"


class Event(BaseModel):
    sensor_id: str
    temperature: float


  