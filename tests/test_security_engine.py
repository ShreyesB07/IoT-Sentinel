"""Unit tests for the IoT Sentinel gateway security rules."""
import tempfile
import unittest
from pathlib import Path

from core.engine import IoTSentinelEngine
from simulator.traffic import command


class SecurityEngineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.engine = IoTSentinelEngine(Path(self.temp_dir.name) / "test.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_authorized_owner_command_changes_actuator(self):
        event = self.engine.process_command(command("owner-app", "smart-light-01", "set_power", True))
        self.assertEqual(event["status"], "ALLOWED")
        light = next(d for d in self.engine.get_devices() if d["device_id"] == "smart-light-01")
        self.assertTrue(light["state"]["power"])

    def test_guest_cannot_unlock_front_door(self):
        event = self.engine.process_command(command("guest-tablet", "smart-lock-01", "unlock"))
        self.assertEqual(event["status"], "BLOCKED")
        self.assertEqual(event["event_type"], "unauthorized_actuator_access")
        door = next(d for d in self.engine.get_devices() if d["device_id"] == "smart-lock-01")
        self.assertTrue(door["state"]["locked"])

    def test_unknown_client_is_blocked(self):
        event = self.engine.process_command(command("fake-controller", "smart-lock-01", "unlock", token="fake"))
        self.assertEqual(event["status"], "BLOCKED")
        self.assertEqual(event["event_type"], "device_impersonation")

    def test_invalid_token_is_blocked(self):
        event = self.engine.process_command(command("owner-app", "smart-fan-01", "set_power", True, token="wrong"))
        self.assertEqual(event["status"], "BLOCKED")
        self.assertEqual(event["event_type"], "invalid_credentials")

    def test_duplicate_request_id_is_replay(self):
        first = command("owner-app", "smart-light-01", "set_power", True, request_id="fixed-request")
        first_event = self.engine.process_command(first)
        second = dict(first)
        second["scenario"] = "replay_attack"
        second["is_attack"] = True
        second_event = self.engine.process_command(second)
        self.assertEqual(first_event["status"], "ALLOWED")
        self.assertEqual(second_event["status"], "BLOCKED")
        self.assertEqual(second_event["event_type"], "replay_attack")

    def test_rate_limiter_blocks_request_over_threshold(self):
        results = []
        for number in range(6):
            results.append(self.engine.process_command(command(
                "owner-app", "smart-light-01", "set_power", bool(number % 2), request_id=f"flood-{number}")))
        self.assertEqual([e["status"] for e in results[:5]], ["ALLOWED"] * 5)
        self.assertEqual(results[5]["status"], "BLOCKED")
        self.assertEqual(results[5]["event_type"], "traffic_flooding")

    def test_sensor_cannot_receive_actuator_command(self):
        event = self.engine.process_command(command("owner-app", "temp-sensor-01", "set_power", True))
        self.assertEqual(event["status"], "BLOCKED")
        self.assertEqual(event["event_type"], "sensor_control_attempt")

    def test_invalid_brightness_value_is_blocked(self):
        event = self.engine.process_command(command("owner-app", "smart-light-01", "set_brightness", 140))
        self.assertEqual(event["status"], "BLOCKED")
        self.assertEqual(event["event_type"], "invalid_command")


if __name__ == "__main__":
    unittest.main(verbosity=2)
