import json
import tempfile
import unittest
from pathlib import Path

from tracker.batches import export_batch, import_batch
from tracker.store import EventStore


class BatchTests(unittest.TestCase):
    def test_valid_assessment_updates_details_without_shortlist(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory)
            store = EventStore(root / "events.sqlite")
            event_id = store.upsert_event(
                source_key="official:event", name="Event", city="Mumbai",
                start_date="2027-01-01", end_date="2027-01-02",
                source_url="https://example.org/event", details={"industry": "Retail"},
            )
            store.set_shortlist(event_id, True)
            batch_path = root / "batch.json"
            export_batch(store, batch_path)
            candidate = json.loads(batch_path.read_text(encoding="utf-8"))["candidates"][0]
            response = root / "response.json"
            response.write_text(json.dumps({"results": [{
                "event_id": event_id,
                "evidence_fingerprint": candidate["evidence_fingerprint"],
                "suitability": "AMBER", "reason": "Mixed exhibitors", "shortlisted": False
            }]}), encoding="utf-8")
            report = import_batch(store, response)
            self.assertEqual(report["accepted"], [event_id])
            self.assertEqual(store.list_events()[0]["details"]["ai_reason"], "Mixed exhibitors")
            self.assertTrue(store.get_shortlist(event_id))
            repeated = import_batch(store, response)
            self.assertEqual(repeated["stale"], [])
            self.assertEqual(repeated["accepted"], [event_id])

    def test_stale_assessment_cannot_replace_newer_event(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory)
            store = EventStore(root / "events.sqlite")
            event_id = store.upsert_event(
                source_key="official:event", name="Event", city="Mumbai",
                start_date="2027-01-01", end_date="2027-01-02",
                source_url="https://example.org/event", details={"industry": "Retail"},
            )
            batch_path = root / "batch.json"
            export_batch(store, batch_path)
            candidate = json.loads(batch_path.read_text(encoding="utf-8"))["candidates"][0]
            store.upsert_event(
                source_key="official:event", name="Event", city="Mumbai",
                start_date="2027-02-01", end_date="2027-02-02",
                source_url="https://example.org/event", details={"industry": "Retail"},
            )
            response = root / "response.json"
            response.write_text(json.dumps({"results": [{
                "event_id": event_id,
                "evidence_fingerprint": candidate["evidence_fingerprint"],
                "suitability": "GREEN", "reason": "Retail brands"
            }]}), encoding="utf-8")
            report = import_batch(store, response)
            self.assertEqual(report["stale"], [event_id])
            self.assertNotIn("ai_reason", store.list_events()[0]["details"])


if __name__ == "__main__":
    unittest.main()
