import os

WORKER_ACCOUNT = os.environ.get("WORKER_ACCOUNT", "")
WORKER_PASSWORD = os.environ.get("WORKER_PASSWORD", "")

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 0))
