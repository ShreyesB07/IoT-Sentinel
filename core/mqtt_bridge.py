"""Optional MQTT publishing bridge for a local Mosquitto broker.

The main simulator is self-contained. Connecting this bridge mirrors events to
an actual MQTT broker on the local machine; it never contacts a remote broker.
"""
from __future__ import annotations

import json
import threading
from typing import Any


class MQTTBridge:
    def __init__(self):
        self.client = None
        self.connected = False
        self.last_error = ""
        self._connected_event = threading.Event()

    def connect(self, host: str = "127.0.0.1", port: int = 1883, timeout: float = 3.0):
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            self.last_error = "Paho MQTT is not installed. Run: pip install -r requirements.txt"
            return False, self.last_error

        self.disconnect()
        try:
            try:
                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="iot-sentinel-dashboard")
            except (AttributeError, TypeError):
                client = mqtt.Client(client_id="iot-sentinel-dashboard")

            def on_connect(_client, _userdata, _flags, reason_code, *extra):
                code = getattr(reason_code, "value", reason_code)
                if code == 0 or str(reason_code).lower() in ("success", "0"):
                    self.connected = True
                    self.last_error = ""
                else:
                    self.connected = False
                    self.last_error = f"Broker rejected the connection: {reason_code}"
                self._connected_event.set()

            def on_disconnect(_client, _userdata, *args):
                self.connected = False

            client.on_connect = on_connect
            client.on_disconnect = on_disconnect
            self._connected_event.clear()
            client.connect(host, int(port), keepalive=30)
            client.loop_start()
            if not self._connected_event.wait(timeout):
                client.loop_stop()
                self.last_error = f"No response from MQTT broker at {host}:{port}. Is Mosquitto running?"
                return False, self.last_error
            if not self.connected:
                client.loop_stop()
                return False, self.last_error or "MQTT connection failed."
            self.client = client
            return True, f"Connected to local MQTT broker at {host}:{port}."
        except Exception as exc:  # Keep the optional feature from breaking the local lab.
            self.last_error = str(exc)
            self.connected = False
            return False, self.last_error

    def publish_event(self, event: dict[str, Any]):
        if not self.connected or self.client is None:
            return False, "MQTT is not connected. The event remains safely stored in the local audit log."
        payload = json.dumps(event, default=str)
        try:
            info = self.client.publish("iot-sentinel/traffic/events", payload, qos=0, retain=False)
            if info.rc != 0:
                return False, f"MQTT publish returned code {info.rc}."
            return True, "Event mirrored to iot-sentinel/traffic/events."
        except Exception as exc:
            return False, str(exc)

    def disconnect(self):
        if self.client is not None:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass
        self.client = None
        self.connected = False
        self._connected_event.clear()

    def status(self):
        return self.connected
