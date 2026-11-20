"""Central configuration for IoT Sentinel.

The credentials below are deliberately public demo credentials for a local,
synthetic lab. Never reuse them in a real deployment.
"""
from pathlib import Path

APP_NAME = "IoT Sentinel"
APP_SUBTITLE = "IoT network security and actuator protection lab"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
DB_PATH = DATA_DIR / "iot_sentinel.db"

MQTT_HOST = "127.0.0.1"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 30
MQTT_TOPIC_ROOT = "iot-sentinel"

RATE_LIMIT_COUNT = 5
RATE_LIMIT_WINDOW_SECONDS = 10

# All credentials are fake examples used only by the local simulator.
CLIENTS = {
    "owner-app": {
        "name": "Home owner app",
        "role": "Owner",
        "token": "demo-owner-token",
        "allowed_targets": ["smart-light-01", "smart-lock-01", "smart-fan-01"],
        "allowed_actions": ["set_power", "set_brightness", "lock", "unlock", "set_speed"],
    },
    "maintenance-console": {
        "name": "Maintenance console",
        "role": "Administrator",
        "token": "demo-maintenance-token",
        "allowed_targets": ["smart-light-01", "smart-lock-01", "smart-fan-01"],
        "allowed_actions": ["set_power", "set_brightness", "lock", "unlock", "set_speed"],
    },
    "guest-tablet": {
        "name": "Guest tablet",
        "role": "Guest",
        "token": "demo-guest-token",
        "allowed_targets": ["smart-light-01"],
        "allowed_actions": ["set_power"],
    },
}

SEVERITY_ORDER = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
