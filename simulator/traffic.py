"""Convenience functions for normal traffic and controlled attack scenarios."""
from __future__ import annotations

import random
import uuid

from config import CLIENTS


def command(source_id: str, target_id: str, action: str, value=None,
            *, token: str | None = None, request_id: str | None = None,
            scenario: str = "manual", is_attack: bool = False):
    client = CLIENTS.get(source_id, {})
    return {
        "request_id": request_id or str(uuid.uuid4()),
        "source_id": source_id,
        "token": token if token is not None else client.get("token", ""),
        "target_id": target_id,
        "action": action,
        "value": value,
        "scenario": scenario,
        "is_attack": is_attack,
    }


def generate_normal_traffic(engine, count: int = 8):
    results = []
    owner_patterns = [
        ("smart-light-01", "set_power", True),
        ("smart-light-01", "set_brightness", 72),
        ("smart-fan-01", "set_speed", 3),
        ("smart-lock-01", "lock", None),
    ]
    engine.clear_rate_window("owner-app")
    engine.clear_rate_window("guest-tablet")
    owner_index = 0
    for i in range(count):
        if i % 2 == 0:
            target, action, value = owner_patterns[owner_index % len(owner_patterns)]
            owner_index += 1
            if action == "set_brightness":
                value = random.choice([55, 65, 72, 80])
            elif action == "set_speed":
                value = random.choice([1, 2, 3, 4])
            elif action == "set_power":
                value = bool(random.getrandbits(1))
            results.append(engine.process_command(command("owner-app", target, action, value, scenario="normal_traffic")))
        else:
            results.append(engine.process_command(command("guest-tablet", "smart-light-01", "set_power", bool(random.getrandbits(1)), scenario="normal_traffic")))
    return results


def run_attack(engine, scenario: str):
    """Run one contained attack demonstration and return its generated events."""
    events = []
    if scenario == "unauthorized_access":
        engine.clear_rate_window("guest-tablet")
        # A registered guest has a valid identity but cannot unlock the front door.
        for _ in range(3):
            events.append(engine.process_command(command(
                "guest-tablet", "smart-lock-01", "unlock", None,
                scenario=scenario, is_attack=True)))
    elif scenario == "device_impersonation":
        events.append(engine.process_command(command(
            "unregistered-controller-77", "smart-lock-01", "unlock", None,
            token="spoofed-demo-token", scenario=scenario, is_attack=True)))
    elif scenario == "replay_attack":
        engine.clear_rate_window("owner-app")
        reused = command("owner-app", "smart-light-01", "set_power", True,
                         scenario="replay_attack_original", is_attack=False)
        events.append(engine.process_command(reused))
        replay = dict(reused)
        replay["scenario"] = scenario
        replay["is_attack"] = True
        events.append(engine.process_command(replay))
    elif scenario == "traffic_flooding":
        engine.clear_rate_window("owner-app")
        for i in range(12):
            events.append(engine.process_command(command(
                "owner-app", "smart-light-01", "set_brightness", 40 + (i % 6) * 10,
                scenario=scenario, is_attack=True)))
    elif scenario == "invalid_credentials":
        events.append(engine.process_command(command(
            "owner-app", "smart-fan-01", "set_power", True,
            token="incorrect-demo-token", scenario=scenario, is_attack=True)))
    else:
        raise ValueError(f"Unknown attack scenario: {scenario}")
    return events
