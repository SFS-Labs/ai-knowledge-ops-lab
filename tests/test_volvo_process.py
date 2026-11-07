"""Volvo original-event-log audits: one case one observation, no pseudo-text labels."""
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "showcases/internal-service-intake/evaluation"))
from volvo_process import summarize_stream, ORIGINAL_MD5  # noqa: E402

XES = b"""<?xml version="1.0" encoding="UTF-8"?>
<log>
<trace>
<string key="concept:name" value="example-A"/>
<event><string key="concept:name" value="In Progress"/><date key="time:timestamp" value="2012-01-01T00:00:00Z"/><string key="org:group" value="group-1"/><string key="impact" value="High"/></event>
<event><string key="concept:name" value="Awaiting Assignment"/><date key="time:timestamp" value="2012-01-01T01:00:00Z"/><string key="org:group" value="group-2"/><string key="impact" value="Low"/></event>
<event><string key="concept:name" value="Closed"/><date key="time:timestamp" value="2012-01-01T02:00:00Z"/><string key="org:group" value="group-2"/></event>
</trace>
<trace>
<string key="concept:name" value="example-B"/>
<event><string key="concept:name" value="Opened"/><date key="time:timestamp" value="2012-01-02T00:00:00Z"/><string key="org:group" value="group-1"/></event>
<event><string key="concept:name" value="Closed"/><date key="time:timestamp" value="2012-01-02T00:00:00Z"/><string key="org:group" value="group-1"/></event>
</trace>
</log>"""


class VolvoResearchTests(unittest.TestCase):
    def test_first_recorded_impact_not_last_or_truth(self):
        result = summarize_stream(io.BytesIO(XES))
        self.assertEqual({"High": 1, "<missing>": 1}, result["observed"]["first_recorded_impact_counts"])
        self.assertEqual(["High", "Low"], result["observed"]["unique_event_impact_values"])

    def test_count_group_transitions_not_elapsed_work(self):
        result = summarize_stream(io.BytesIO(XES))["observed"]
        self.assertEqual(2, result["incident_cases"])
        self.assertEqual(5, result["events"])
        self.assertEqual(1, result["total_observed_group_transitions"])
        self.assertEqual(0.5, result["fraction_cases_with_at_least_one_transition"])
        self.assertEqual(1, result["median_observed_elapsed_hours"])

    def test_genuine_checksum_is_explicit(self):
        self.assertEqual("d4809bd55e3e1c15b017ab4e58228297", ORIGINAL_MD5)

    def test_empty_stream_fails(self):
        with self.assertRaises(ValueError):
            summarize_stream(io.BytesIO(b"<log/>"))


if __name__ == "__main__":
    unittest.main()
