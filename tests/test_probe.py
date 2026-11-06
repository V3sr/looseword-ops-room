"""End-to-end check: start the simulator, probe every target, check outcomes.

Run from the repo root:  python -m unittest discover -s tests -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sim"))
sys.path.insert(0, str(ROOT / "tools"))

import intake_sim  # noqa: E402
import probe  # noqa: E402


def by_name(results):
    return {r["name"]: r for r in results}


class OutageScenario(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servers = intake_sim.serve("outage")
        cls.results = by_name(probe.probe(t) for t in probe.load_targets())

    @classmethod
    def tearDownClass(cls):
        for s in cls.servers:
            s.shutdown()
            s.server_close()

    def test_failing_target_reports_503(self):
        r = self.results["ubc-test"]
        self.assertEqual(r["status"], 503)
        self.assertEqual(r["outcome"], "failing")
        self.assertIn("form_backend_timeout", r["detail"])
        self.assertGreaterEqual(r["latency_ms"], 1000)

    def test_healthy_target_reports_200(self):
        r = self.results["vanier-test"]
        self.assertEqual(r["status"], 200)
        self.assertEqual(r["outcome"], "healthy")

    def test_unavailable_target_is_unreachable(self):
        r = self.results["orchard-test"]
        self.assertIsNone(r["status"])
        self.assertEqual(r["outcome"], "unreachable")


class RecoveredScenario(unittest.TestCase):
    def test_ubc_recovers(self):
        servers = intake_sim.serve("recovered")
        try:
            target = next(t for t in probe.load_targets() if t["name"] == "ubc-test")
            r = probe.probe(target)
        finally:
            for s in servers:
                s.shutdown()
                s.server_close()
        self.assertEqual(r["status"], 200)
        self.assertEqual(r["outcome"], "healthy")


class Guardrails(unittest.TestCase):
    def test_non_local_url_is_refused(self):
        r = probe.probe({"name": "live", "url": "https://looseword.ca/"})
        self.assertEqual(r["outcome"], "refused")
        self.assertIsNone(r["status"])


if __name__ == "__main__":
    unittest.main()
