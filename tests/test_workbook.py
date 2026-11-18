import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from tracker.store import EventStore
from tracker.workbook import export_workbook, import_shortlist


class WorkbookTests(unittest.TestCase):
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
