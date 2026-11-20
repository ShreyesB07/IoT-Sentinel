"""Command validation, actuator simulation and security event generation."""
from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
import time
import uuid
from typing import Any

from config import CLIENTS, RATE_LIMIT_COUNT, RATE_LIMIT_WINDOW_SECONDS
from security.rules import THREAT_RULES
from simulator.devices import get_devices
from core.store import EventStore


class IoTSentinelEngine:
    """A deterministic, local simulation of an IoT gateway security layer."""

    def __init__(self, db_path: str | Path):
        self.store = EventStore(db_path)
        self.devices = {d["device_id"]: d for d in get_devices()}
        self.seen_request_ids: set[str] = set()
        self.recent_requests: dict[str, deque[float]] = defaultdict(deque)

    @staticmethod
    def new_request_id() -> str:
        return str(uuid.uuid4())

    def get_devices(self):
        return [dict(d, state=dict(d["state"])) for d in self.devices.values()]

    def _event(self, command: dict[str, Any], status: str, severity: str,
               event_type: str, reason: str, detected: bool) -> dict[str, Any]:
        return {
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "request_id": str(command.get("request_id") or self.new_request_id()),
            "source_id": str(command.get("source_id", "unknown")),
            "target_id": str(command.get("target_id", "unknown")),
            "action": str(command.get("action", "unknown")),
            "value": command.get("value"),
            "status": status,
            "severity": severity,
            "event_type": event_type,
            "reason": reason,
            "scenario": str(command.get("scenario", "manual")),
            "is_attack": bool(command.get("is_attack", False)),
            "detected": bool(detected),
            "transport": str(command.get("transport", "SIMULATED")),
        }

    def _finish(self, event: dict[str, Any]):
        self.store.add_event(event)
        return event

    def process_command(self, command: dict[str, Any]) -> dict[str, Any]:
        """Validate and apply one command. Every request is written to the audit log."""
        command = dict(command)
        command.setdefault("request_id", self.new_request_id())
        source_id = str(command.get("source_id", "unknown"))
        token = str(command.get("token", ""))

        client = CLIENTS.get(source_id)
        if client is None:
            info = THREAT_RULES["device_impersonation"]
            return self._finish(self._event(command, "BLOCKED", info["severity"],
                "device_impersonation", info["explanation"], True))

        if token != client["token"]:
            info = THREAT_RULES["invalid_credentials"]
            return self._finish(self._event(command, "BLOCKED", info["severity"],
                "invalid_credentials", info["explanation"], True))

        request_id = str(command["request_id"])
        if request_id in self.seen_request_ids:
            info = THREAT_RULES["replay_attack"]
            return self._finish(self._event(command, "BLOCKED", info["severity"],
                "replay_attack", info["explanation"], True))
        self.seen_request_ids.add(request_id)

        now = time.monotonic()
        recent = self.recent_requests[source_id]
        while recent and now - recent[0] > RATE_LIMIT_WINDOW_SECONDS:
            recent.popleft()
        recent.append(now)
        if len(recent) > RATE_LIMIT_COUNT:
            info = THREAT_RULES["traffic_flooding"]
            reason = (f"{len(recent)} requests from this client were observed within "
                      f"{RATE_LIMIT_WINDOW_SECONDS} seconds; the configured limit is "
                      f"{RATE_LIMIT_COUNT}.")
            return self._finish(self._event(command, "BLOCKED", info["severity"],
                "traffic_flooding", reason, True))

        target_id = str(command.get("target_id", ""))
        device = self.devices.get(target_id)
        if device is None:
            info = THREAT_RULES["invalid_command"]
            return self._finish(self._event(command, "BLOCKED", info["severity"],
                "invalid_command", "The requested target is not registered in this lab.", bool(command.get("is_attack"))))

        if not device["actuator"]:
            info = THREAT_RULES["sensor_control_attempt"]
            return self._finish(self._event(command, "BLOCKED", info["severity"],
                "sensor_control_attempt", info["explanation"], bool(command.get("is_attack"))))

        action = str(command.get("action", ""))
        if target_id not in client["allowed_targets"] or action not in client["allowed_actions"]:
            info = THREAT_RULES["unauthorized_actuator_access"]
            reason = (f"Client '{source_id}' ({client['role']}) is not permitted to run "
                      f"'{action}' on '{target_id}'.")
            return self._finish(self._event(command, "BLOCKED", info["severity"],
                "unauthorized_actuator_access", reason, True))

        if action not in device["actions"]:
            info = THREAT_RULES["invalid_command"]
            reason = f"The device does not support the action '{action}'."
            return self._finish(self._event(command, "BLOCKED", info["severity"],
                "invalid_command", reason, bool(command.get("is_attack"))))

        valid, value_reason = self._validate_value(action, command.get("value"))
        if not valid:
            info = THREAT_RULES["invalid_command"]
            return self._finish(self._event(command, "BLOCKED", info["severity"],
                "invalid_command", value_reason, bool(command.get("is_attack"))))

        self._apply_action(device, action, command.get("value"))
        event = self._event(command, "ALLOWED", "INFO", "authorized_command",
                            f"Accepted: {client['role']} is authorised to run '{action}' on {device['name']}.",
                            False)
        return self._finish(event)

    @staticmethod
    def _validate_value(action: str, value: Any):
        if action == "set_power" and isinstance(value, bool):
            return True, ""
        if action == "set_brightness":
            if isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 100:
                return True, ""
            return False, "Brightness must be a whole number from 0 to 100."
        if action == "set_speed":
            if isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 5:
                return True, ""
            return False, "Fan speed must be a whole number from 0 to 5."
        if action in ("lock", "unlock"):
            return True, ""
        return False, f"No validation rule exists for action '{action}'."

    @staticmethod
    def _apply_action(device: dict[str, Any], action: str, value: Any):
        if action == "set_power":
            device["state"]["power"] = bool(value)
        elif action == "set_brightness":
            device["state"]["brightness"] = int(value)
        elif action == "set_speed":
            device["state"]["speed"] = int(value)
            device["state"]["power"] = int(value) > 0
        elif action == "lock":
            device["state"]["locked"] = True
        elif action == "unlock":
            device["state"]["locked"] = False

    def clear_rate_window(self, source_id: str):
        """Start a clean, repeatable rate-limit demonstration for one source."""
        self.recent_requests[source_id].clear()

    def reset_lab(self):
        """Clear the event history and restore all simulated state and replay memory."""
        self.store.clear()
        self.devices = {d["device_id"]: d for d in get_devices()}
        self.seen_request_ids.clear()
        self.recent_requests.clear()

    def summary(self):
        return self.store.metrics()
