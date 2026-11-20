"""Integration checks for each button in the Attack simulation lab."""
import tempfile
import unittest
from pathlib import Path

from core.engine import IoTSentinelEngine
from simulator.traffic import run_attack


class AttackScenarioTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.engine = IoTSentinelEngine(Path(self.temp_dir.name) / "scenarios.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_unauthorized_access_scenario_is_blocked(self):
        events = run_attack(self.engine, "unauthorized_access")
        self.assertEqual(len(events), 3)
        self.assertTrue(all(e["status"] == "BLOCKED" for e in events))
        self.assertTrue(all(e["event_type"] == "unauthorized_actuator_access" for e in events))

    def test_impersonation_scenario_is_blocked(self):
        events = run_attack(self.engine, "device_impersonation")
        self.assertEqual(events[0]["event_type"], "device_impersonation")
        self.assertEqual(events[0]["status"], "BLOCKED")

    def test_replay_scenario_accepts_original_and_blocks_duplicate(self):
        events = run_attack(self.engine, "replay_attack")
        self.assertEqual([e["status"] for e in events], ["ALLOWED", "BLOCKED"])
        self.assertEqual(events[1]["event_type"], "replay_attack")

    def test_flooding_scenario_blocks_requests_above_limit(self):
        events = run_attack(self.engine, "traffic_flooding")
        self.assertEqual(len(events), 12)
        self.assertEqual(sum(e["status"] == "ALLOWED" for e in events), 5)
        self.assertEqual(sum(e["event_type"] == "traffic_flooding" for e in events), 7)

    def test_invalid_credentials_scenario_is_blocked(self):
        events = run_attack(self.engine, "invalid_credentials")
        self.assertEqual(events[0]["status"], "BLOCKED")
        self.assertEqual(events[0]["event_type"], "invalid_credentials")


if __name__ == "__main__":
    unittest.main(verbosity=2)
