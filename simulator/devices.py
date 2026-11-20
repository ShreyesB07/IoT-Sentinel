"""Definitions and initial state for the virtual IoT installation."""
from copy import deepcopy

DEVICE_TEMPLATES = [
    {
        "device_id": "gateway-01",
        "name": "Main IoT gateway",
        "kind": "Gateway",
        "role": "Network coordinator",
        "zone": "Utility room",
        "description": "Routes messages between the virtual devices and the security monitor.",
        "actuator": False,
        "actions": [],
        "initial_state": {"status": "Online"},
    },
    {
        "device_id": "temp-sensor-01",
        "name": "Temperature sensor",
        "kind": "Sensor",
        "role": "Environmental sensor",
        "zone": "Living room",
        "description": "Reports room temperature. It does not accept control commands.",
        "actuator": False,
        "actions": [],
        "initial_state": {"temperature_c": 24.5, "status": "Online"},
    },
    {
        "device_id": "humidity-sensor-01",
        "name": "Humidity sensor",
        "kind": "Sensor",
        "role": "Environmental sensor",
        "zone": "Kitchen",
        "description": "Reports relative humidity. It does not accept control commands.",
        "actuator": False,
        "actions": [],
        "initial_state": {"humidity_pct": 48, "status": "Online"},
    },
    {
        "device_id": "smart-light-01",
        "name": "Smart ceiling light",
        "kind": "Actuator",
        "role": "Lighting control",
        "zone": "Living room",
        "description": "Can be switched on/off and have its brightness adjusted.",
        "actuator": True,
        "actions": ["set_power", "set_brightness"],
        "initial_state": {"power": False, "brightness": 65, "status": "Online"},
    },
    {
        "device_id": "smart-lock-01",
        "name": "Front door lock",
        "kind": "Actuator",
        "role": "Door access control",
        "zone": "Entrance",
        "description": "Can be locked or unlocked by an authorised controller.",
        "actuator": True,
        "actions": ["lock", "unlock"],
        "initial_state": {"locked": True, "status": "Online"},
    },
    {
        "device_id": "smart-fan-01",
        "name": "Ceiling fan",
        "kind": "Actuator",
        "role": "Climate control",
        "zone": "Bedroom",
        "description": "Can be switched on/off and have its speed adjusted.",
        "actuator": True,
        "actions": ["set_power", "set_speed"],
        "initial_state": {"power": False, "speed": 2, "status": "Online"},
    },
]


def get_devices():
    """Return a fresh copy so one session cannot mutate the templates."""
    devices = deepcopy(DEVICE_TEMPLATES)
    for device in devices:
        device["state"] = deepcopy(device.pop("initial_state"))
    return devices


def get_device_map():
    return {device["device_id"]: device for device in get_devices()}
