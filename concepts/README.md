# Concept Scripts Setup

This directory contains individual concept scripts demonstrating core features of the workshop

## 1. Create Python Virtual Environment

It is recommended to run these scripts in an isolated environment.

# 1. Install Pyenv (Recommended)
# This ensures you use a consistent Python version
pyenv install 3.11.9
pyenv local 3.11.9

# 2. Creates virtual environment
python -m venv venv

# 3. Activate environment
# On Mac/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

## 2. Install Dependencies

Upgrade pip and install required libraries.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Run a Concept Script

Each script is standalone. You can run them directly with Python or Uvicorn (for API scripts).

**Example: CRUD with DB**
```bash
# Ensure your Postgres container is running!
# docker-compose up -d postgres

uvicorn 01_crud_with_db:app --reload --port 9001
```

**Example: Kafka Producer/Consumer**
```bash
# Ensure Kafka container is running!
# docker-compose up -d kafka

python 03_kafka_producer_consumer.py
```

