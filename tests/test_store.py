import tempfile
import unittest
import sqlite3
from contextlib import closing
from pathlib import Path

from tracker.store import EventStore


class EventStoreTests(unittest.TestCase):
    def test_event_identity_and_shortlist_survive_reschedule(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            store = EventStore(Path(directory) / "events.sqlite")
            event_id = store.upsert_event(
                source_key="official:book-fair-2027",
                name="World Book Fair 2027",
                city="New Delhi",
                start_date="2027-01-16",
                end_date="2027-01-24",
                source_url="https://example.org/event",
            )
            store.set_shortlist(event_id, True)
            updated_id = store.upsert_event(
                source_key="official:book-fair-2027",
                name="World Book Fair 2027",
                city="New Delhi",
                start_date="2027-02-16",
                end_date="2027-02-24",
                source_url="https://example.org/event",
            )
            self.assertEqual(updated_id, event_id)
            self.assertTrue(store.get_shortlist(event_id))
            self.assertEqual(store.list_events()[0]["start_date"], "2027-02-16")

    def test_event_details_are_saved_with_the_source(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            store = EventStore(Path(directory) / "events.sqlite")
            store.upsert_event(
                source_key="official:imtex-2027", name="IMTEX 2027",
                city="Bengaluru", start_date="2027-01-21",
                end_date="2027-01-27", source_url="https://www.imtex.in/home",
                details={"edition": "22nd", "exhibitors": "1,200+"},
            )
            self.assertEqual(store.list_events()[0]["details"]["edition"], "22nd")

    def test_existing_database_gains_details_without_losing_shortlist(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            path = Path(directory) / "events.sqlite"
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute("CREATE TABLE events (event_id TEXT PRIMARY KEY, source_key TEXT UNIQUE, name TEXT, city TEXT, start_date TEXT, end_date TEXT, source_url TEXT, shortlisted INTEGER)")
                connection.execute("INSERT INTO events VALUES ('existing', 'official:old', 'Old Fair', 'Mumbai', '2027-01-01', NULL, 'https://example.org', 1)")
            store = EventStore(path)
            self.assertTrue(store.get_shortlist("existing"))
            self.assertEqual(store.list_events()[0]["details"], {})


if __name__ == "__main__":
    unittest.main()
