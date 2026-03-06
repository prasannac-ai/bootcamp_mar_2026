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


  
# Kafka Event Producer
class KafkaEventProducer:
  

    def __init__(self, bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    # Start Kafka producer
    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
        )
        await self.producer.start()
     
    # Stop Kafka producer
    async def stop(self):
        if self.producer:
            await self.producer.stop()
            
    # Send event to Kafka topic
    async def send_event(self, event: Event, topic: str = TOPIC_NAME):
        event_dict = event.model_dump()
        result = await self.producer.send_and_wait(
            topic=topic,
            value=event_dict,
            key=event.sensor_id,
        )
        return {"topic": topic, "partition": result.partition, "offset": result.offset}

    async def publish_events(self, event: Event):
        await self.start()
        result = await self.send_event(event)
        print(result)
        await asyncio.sleep(0.5)
        await self.stop()


