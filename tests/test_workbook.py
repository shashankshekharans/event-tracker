import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpyxl import Workbook, load_workbook

from tracker.store import EventStore
from tracker.workbook import _add_source_health, export_workbook, import_shortlist


class WorkbookTests(unittest.TestCase):
    def test_source_health_lists_registered_source_without_crawl_log(self):
        source = {"id": "ficci-events", "url": "https://www.ficci.in/event",
                  "publisher": "FICCI", "enabled": True, "permitted_use": "ALLOW",
                  "permission_reason": "Public event facts"}
        with patch("tracker.workbook._load_json") as load:
            load.side_effect = lambda path, default: [source] if path.name == "source_pages.json" else {}
            workbook = Workbook()
            _add_source_health(workbook, [])
        rows = list(workbook["Source Health"].values)
        self.assertEqual(rows[1][0], "ficci-events")
        self.assertEqual(rows[1][4], "NO CRAWL LOG")
        self.assertEqual(rows[1][6], "ENABLED")

    def test_source_health_uses_current_registry_reason(self):
        source = {"id": "whr-ai", "url": "https://whr.ai/",
                  "publisher": "WHR.AI", "enabled": False,
                  "permitted_use": "DISALLOW", "permission_reason": "Current API limits"}
        report = {"sources": [{"source_id": "whr-ai", "url": source["url"],
                               "outcome": "BLOCKED", "error": "Old pricing note",
                               "permission_reason": "Old pricing note"}]}
        with patch("tracker.workbook._load_json") as load:
            load.side_effect = lambda path, default: [source] if path.name == "source_pages.json" else report
            workbook = Workbook()
            _add_source_health(workbook, [])
        notes = list(workbook["Source Health"].values)[1][8]
        self.assertIn("Current API limits", notes)
        self.assertNotIn("Old pricing note", notes)

    def test_shortlist_mark_round_trip(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root = Path(directory)
            store = EventStore(root / "events.sqlite")
            event_id = store.upsert_event(
                source_key="official:imtex-2027", name="IMTEX 2027",
                city="Bengaluru", start_date="2027-01-21",
                end_date="2027-01-27", source_url="https://www.imtex.in/home",
                details={"industry": "Manufacturing", "edition": "22nd"},
            )
            workbook_path = root / "events.xlsx"
            export_workbook(store, workbook_path)
            workbook = load_workbook(workbook_path)
            self.assertIn("Events", workbook.sheetnames)
            self.assertIn("Source Health", workbook.sheetnames)
            urls = {row[2] for row in workbook["Source Health"].iter_rows(min_row=2, values_only=True)}
            self.assertIn("https://www.imtex.in/home", urls)
            self.assertEqual(workbook["Events"].cell(2, 1).value, event_id)
            workbook["Events"].cell(2, 2).value = "Yes"
            workbook.save(workbook_path)
            import_shortlist(store, workbook_path)
            export_workbook(store, workbook_path)
            self.assertTrue(store.get_shortlist(event_id))
            self.assertEqual(load_workbook(workbook_path)["Events"].cell(2, 2).value, "Yes")


if __name__ == "__main__":
    unittest.main()
