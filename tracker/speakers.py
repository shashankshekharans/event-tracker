"""Load source-backed speaker-call records into the local event store."""

import json
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from tracker.store import EventStore


def validate_speaker_input(event_records: list[dict], input_path: Path) -> list[dict]:
    records = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Speaker input must be a JSON list")
    event_keys = {record.get("key") for record in event_records}
    for record in records:
        if record.get("key") not in event_keys:
            raise ValueError(f"Unknown event key in speaker data: {record.get('key')}")
        if record.get("status", "UNKNOWN") not in {"OPEN", "UPCOMING", "CLOSED", "UNKNOWN", "NOT_APPLICABLE"}:
            raise ValueError(f"Invalid speaker opportunity status: {record.get('status')}")
        if record.get("deadline"):
            date.fromisoformat(record["deadline"])
        for field in ("application_url", "evidence_url"):
            url = record.get(field, "")
            if url:
                parsed = urlsplit(url)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    raise ValueError(f"Invalid {field}: {url}")
    return records


def refresh_speaker_opportunities(store: EventStore, input_path: Path) -> int:
    records = json.loads(input_path.read_text(encoding="utf-8"))
    events = {event["source_key"]: event["event_id"] for event in store.list_events()}
    count = 0
    for record in records:
        key = record["key"]
        if key not in events:
            raise ValueError(f"Unknown event key in speaker data: {key}")
        checked = record.get("last_checked", "")
        if checked:
            date.fromisoformat(checked)
        store.upsert_speaker_opportunity(
            opportunity_id=record.get("opportunity_id"), event_id=events[key], status=record.get("status", "UNKNOWN"),
            session_type=record.get("session_type", ""), topic=record.get("topic", ""),
            eligibility=record.get("eligibility", ""),
            application_url=record.get("application_url", ""), deadline=record.get("deadline"),
            contact=record.get("contact", ""), evidence_url=record.get("evidence_url", ""),
            last_checked=checked, missing_information=record.get("missing_information", ""),
        )
        count += 1
    return count
