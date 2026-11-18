import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from tracker.cli import refresh_from_file, run_scan


class RefreshTests(unittest.TestCase):
    def test_scan_records_candidate_links(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            output = Path(directory) / "discovered.json"
            result = run_scan(
                [{"id": "fixture", "url": "https://events.example", "enabled": True,
                  "permitted_use": "ALLOW", "max_depth": 0}], output,
                fetch_html=lambda url: '<a href="/fashion-expo-2027">Fashion Expo 2027</a>',
            )
            self.assertEqual(result["candidate_links"], ["https://events.example/fashion-expo-2027"])
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), result)

    def test_refresh_keeps_marks_after_date_change(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory)
            seed = root / "seed.json"
            seed.write_text(json.dumps([{
                "key": "fair-2027", "name": "Fair 2027", "city": "Mumbai",
                "start": "2027-01-01", "end": "2027-01-02",
                "url": "https://example.org/fair", "details": {}
            }]), encoding="utf-8")
            output = root / "events.xlsx"
            refresh_from_file(root / "events.sqlite", seed, output)
            workbook = load_workbook(output)
            workbook["Events"]["B2"] = "Yes"
            workbook.save(output)
            records = json.loads(seed.read_text(encoding="utf-8"))
            records[0]["start"] = "2027-02-01"
            records[0]["end"] = "2027-02-02"
            seed.write_text(json.dumps(records), encoding="utf-8")
            refresh_from_file(root / "events.sqlite", seed, output)
            refreshed = load_workbook(output)["Events"]
            self.assertEqual(refreshed["B2"].value, "Yes")
            self.assertEqual(refreshed["F2"].value.date().isoformat(), "2027-02-01")

    def test_invalid_input_does_not_partially_update_events(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory)
            seed = root / "seed.json"
            seed.write_text(json.dumps([
                {"key": "valid", "name": "Valid Fair", "city": "Mumbai", "start": "2027-01-01", "end": "2027-01-02", "url": "https://example.org/a", "details": {}},
                {"key": "bad", "name": "Bad Fair", "city": "Mumbai", "start": "2027-03-03", "end": "2027-03-01", "url": "https://example.org/b", "details": {}}
            ]), encoding="utf-8")
            with self.assertRaises(ValueError):
                refresh_from_file(root / "events.sqlite", seed, root / "events.xlsx")
            from tracker.store import EventStore
            self.assertEqual(EventStore(root / "events.sqlite").list_events(), [])


if __name__ == "__main__":
    unittest.main()
