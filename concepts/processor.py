"""
Simple Kafka Consumer Utility
"""

import asyncio
import json

from pydantic import BaseModel
from aiokafka import AIOKafkaConsumer
from ingestion import Event
from irrigation_service import IrrigationService

from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
TOPIC_NAME = "sensor.events"
CONSUMER_GROUP = "sensor_data_group"


