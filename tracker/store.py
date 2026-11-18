"""Durable event identities and shortlist marks."""

import sqlite3
import uuid
import json
from urllib.parse import urlsplit
from contextlib import closing
from datetime import date
from pathlib import Path

from tracker.event_status import is_scheduled


class EventStore:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS events (
                    event_id TEXT PRIMARY KEY,
                    source_key TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    city TEXT NOT NULL,
                    start_date TEXT,
                    end_date TEXT,
                    source_url TEXT NOT NULL,
                    details_json TEXT NOT NULL DEFAULT '{}',
                    shortlisted INTEGER NOT NULL DEFAULT 0
                )"""
            )
            columns = {row[1] for row in connection.execute("PRAGMA table_info(events)")}
            if "details_json" not in columns:
                connection.execute(
                    "ALTER TABLE events ADD COLUMN details_json TEXT NOT NULL DEFAULT '{}'"
                )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS speaker_opportunities (
                    opportunity_id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL REFERENCES events(event_id),
                    shortlisted INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'UNKNOWN',
                    session_type TEXT NOT NULL DEFAULT '',
                    topic TEXT NOT NULL DEFAULT '',
                    eligibility TEXT NOT NULL DEFAULT '',
                    application_url TEXT NOT NULL DEFAULT '',
                    deadline TEXT,
                    contact TEXT NOT NULL DEFAULT '',
                    evidence_url TEXT NOT NULL DEFAULT '',
                    last_checked TEXT NOT NULL DEFAULT '',
                    missing_information TEXT NOT NULL DEFAULT ''
                )"""
            )

    def _connect(self):
        return sqlite3.connect(self.path)

    def upsert_event(self, *, source_key: str, name: str, city: str,
                     start_date: str | None, end_date: str | None,
                     source_url: str, details: dict | None = None) -> str:
        if start_date and end_date and end_date < start_date:
            raise ValueError("End date precedes start date")
        with closing(self._connect()) as connection, connection:
            event = connection.execute(
                "SELECT event_id FROM events WHERE source_key = ?", (source_key,)
            ).fetchone()
            event_id = event[0] if event else uuid.uuid4().hex
            connection.execute(
                """INSERT INTO events
                (event_id, source_key, name, city, start_date, end_date, source_url, details_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_key) DO UPDATE SET
                    name = excluded.name,
                    city = excluded.city,
                    start_date = excluded.start_date,
                    end_date = excluded.end_date,
                    source_url = excluded.source_url,
                    details_json = excluded.details_json""",
                (event_id, source_key, name, city, start_date, end_date, source_url,
                 json.dumps(details or {}, ensure_ascii=False)),
            )
        return event_id

    def set_shortlist(self, event_id: str, marked: bool) -> None:
        with closing(self._connect()) as connection, connection:
            cursor = connection.execute(
                "UPDATE events SET shortlisted = ? WHERE event_id = ?",
                (int(marked), event_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(event_id)

    def get_shortlist(self, event_id: str) -> bool:
        with closing(self._connect()) as connection, connection:
            result = connection.execute(
                "SELECT shortlisted FROM events WHERE event_id = ?", (event_id,)
            ).fetchone()
        if result is None:
            raise KeyError(event_id)
        return bool(result[0])

    def list_events(self) -> list[dict]:
        with closing(self._connect()) as connection, connection:
            connection.row_factory = sqlite3.Row
            events = [dict(row) for row in connection.execute(
                "SELECT * FROM events ORDER BY start_date, city, name"
            )]
        for event in events:
            event["details"] = json.loads(event.pop("details_json"))
        return events

    def update_assessment(self, event_id: str, suitability: str, reason: str) -> None:
        with closing(self._connect()) as connection, connection:
            row = connection.execute(
                "SELECT details_json FROM events WHERE event_id = ?", (event_id,)
            ).fetchone()
            if row is None:
                raise KeyError(event_id)
            details = json.loads(row[0])
            details["suitability"] = suitability
            details["ai_reason"] = reason
            connection.execute(
                "UPDATE events SET details_json = ? WHERE event_id = ?",
                (json.dumps(details, ensure_ascii=False), event_id),
            )

    def upsert_speaker_opportunity(self, *, opportunity_id: str | None = None,
                                   event_id: str, status: str = "UNKNOWN",
                                   session_type: str = "", topic: str = "",
                                   eligibility: str = "", application_url: str = "",
                                   deadline: str | None = None, contact: str = "",
                                   evidence_url: str = "", last_checked: str = "",
                                   missing_information: str = "") -> str:
        allowed = {"OPEN", "UPCOMING", "CLOSED", "UNKNOWN", "NOT_APPLICABLE"}
        if status not in allowed:
            raise ValueError(f"Invalid speaker opportunity status: {status}")
        if deadline:
            date.fromisoformat(deadline)
        for field_name, url in (("application_url", application_url), ("evidence_url", evidence_url)):
            if url:
                parsed = urlsplit(url)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    raise ValueError(f"Invalid {field_name}: {url}")
        with closing(self._connect()) as connection, connection:
            if connection.execute("SELECT 1 FROM events WHERE event_id = ?", (event_id,)).fetchone() is None:
                raise KeyError(event_id)
            existing = None
            if opportunity_id:
                existing = connection.execute("SELECT opportunity_id,event_id FROM speaker_opportunities WHERE opportunity_id = ?", (opportunity_id,)).fetchone()
                if existing and existing[1] != event_id:
                    raise ValueError("An opportunity ID cannot be moved to another event edition")
            else:
                existing = connection.execute("SELECT opportunity_id,event_id FROM speaker_opportunities WHERE event_id = ? AND application_url = ? AND session_type = ? AND topic = ?", (event_id, application_url, session_type, topic)).fetchone()
            identifier = existing[0] if existing else (opportunity_id or uuid.uuid4().hex)
            connection.execute(
                """INSERT INTO speaker_opportunities
                (opportunity_id,event_id,status,session_type,topic,eligibility,application_url,deadline,contact,evidence_url,last_checked,missing_information)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(opportunity_id) DO UPDATE SET event_id=excluded.event_id,status=excluded.status,
                session_type=excluded.session_type,topic=excluded.topic,eligibility=excluded.eligibility,
                application_url=excluded.application_url,deadline=excluded.deadline,contact=excluded.contact,
                evidence_url=excluded.evidence_url,last_checked=excluded.last_checked,
                missing_information=excluded.missing_information""",
                (identifier,event_id,status,session_type,topic,eligibility,application_url,deadline,contact,evidence_url,last_checked,missing_information),
            )
        return identifier

    def set_speaker_shortlist(self, opportunity_id: str, marked: bool) -> None:
        with closing(self._connect()) as connection, connection:
            cursor = connection.execute("UPDATE speaker_opportunities SET shortlisted=? WHERE opportunity_id=?", (int(marked), opportunity_id))
            if cursor.rowcount != 1:
                raise KeyError(opportunity_id)

    def list_speaker_opportunities(self) -> list[dict]:
        with closing(self._connect()) as connection, connection:
            connection.row_factory = sqlite3.Row
            rows = [dict(row) for row in connection.execute(
                """SELECT s.*, e.source_key, e.name AS event_name, e.city AS event_city,
                e.start_date AS event_start_date, e.end_date AS event_end_date, e.details_json
                FROM speaker_opportunities s JOIN events e USING(event_id)
                ORDER BY e.start_date, e.name, s.session_type"""
            )]
        today = date.today().isoformat()
        for row in rows:
            details = json.loads(row.pop("details_json"))
            event = {"start_date": row["event_start_date"], "details": details}
            event_end = row["event_end_date"] or row["event_start_date"]
            deadline_passed = bool(row["deadline"] and row["deadline"] < today)
            event_ended = is_scheduled(event) and event_end < today
            if row["status"] in {"OPEN", "UPCOMING"} and (deadline_passed or event_ended):
                row["status"] = "CLOSED"
        return rows

    def speaker_status_by_event(self, opportunities: list[dict] | None = None) -> dict[str, str]:
        priorities = {"OPEN": 0, "UPCOMING": 1, "UNKNOWN": 2, "CLOSED": 3, "NOT_APPLICABLE": 4}
        summary = {}
        for item in self.list_speaker_opportunities() if opportunities is None else opportunities:
            current = summary.get(item["event_id"])
            if current is None or priorities[item["status"]] < priorities[current]:
                summary[item["event_id"]] = item["status"]
        return summary
