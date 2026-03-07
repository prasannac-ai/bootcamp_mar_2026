"""
Simple Kafka Consumer Utility
"""

import asyncio
import json

from pydantic import BaseModel
from aiokafka import AIOKafkaConsumer

KAFKA_BOOTSTRAP_SERVERS = "localhost:9094"
TOPIC_NAME = "farmer.events"
CONSUMER_GROUP = "disease_detect_group"


class Event(BaseModel):
    event_type: str
    payload: str


class KafkaEventConsumer:
    def __init__(self, bootstrap_servers: str = KAFKA_BOOTSTRAP_SERVERS):
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            TOPIC_NAME,
            bootstrap_servers=self.bootstrap_servers,
            group_id=CONSUMER_GROUP,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
        )
        await self.consumer.start()

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()

    async def consume(self):
        async for msg in self.consumer:
            event = Event(**msg.value)
            print(f"   {event.event_type} → {event.payload}", flush=True)

# consume events
async def run_consumer_demo():

    consumer = KafkaEventConsumer()
    await consumer.start()
    await consumer.consume()
    await consumer.stop()


if __name__ == "__main__":
    asyncio.run(run_consumer_demo())
