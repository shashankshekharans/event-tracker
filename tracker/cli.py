"""Commands for the local Event Tracker."""

import argparse
import json
import shutil
from datetime import date
from pathlib import Path

from tracker.store import EventStore
from tracker.workbook import export_workbook, import_shortlist, import_speaker_shortlist
from tracker.event_status import is_scheduled
from tracker.collect import SourceSpec, scan_sources, fetch_html, write_scan_result
from tracker.speakers import refresh_speaker_opportunities, validate_speaker_input
from tracker.candidates import stage_candidates


def refresh_from_file(database_path: Path, input_path: Path, workbook_path: Path,
                      speaker_input_path: Path | None = None) -> int:
    records = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Event input must be a JSON list")
    keys = set()
    for record in records:
        for field in ("key", "name", "city", "url"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError(f"Missing event field: {field}")
        if record["key"] in keys:
            raise ValueError(f"Duplicate event key: {record['key']}")
        keys.add(record["key"])
        start = date.fromisoformat(record["start"]) if record.get("start") else None
        end = date.fromisoformat(record["end"]) if record.get("end") else None
        if start and end and end < start:
            raise ValueError(f"End date precedes start date: {record['key']}")
    use_project_data = input_path.resolve() == Path("data/verified_events.json").resolve()
    if speaker_input_path is None and use_project_data:
        default_speaker_path = Path("data/speaker_opportunities.json")
        speaker_input_path = default_speaker_path if default_speaker_path.exists() else None
    if speaker_input_path is not None:
        validate_speaker_input(records, speaker_input_path)
    leadership_path = Path("data/leadership_opportunities.json")
    leadership = json.loads(leadership_path.read_text(encoding="utf-8")) if use_project_data and leadership_path.exists() else []
    store = EventStore(database_path)
    if workbook_path.exists():
        import_shortlist(store, workbook_path)
        import_speaker_shortlist(store, workbook_path)
        shutil.copy2(workbook_path, workbook_path.with_suffix(".previous.xlsx"))
    for record in records:
        store.upsert_event(
            source_key=record["key"], name=record["name"], city=record["city"],
            start_date=record.get("start"), end_date=record.get("end"),
            source_url=record["url"], details=record.get("details", {}),
        )
    if speaker_input_path is not None:
        refresh_speaker_opportunities(store, speaker_input_path)
    export_workbook(store, workbook_path, leadership)
    return len(records)


def run_scan(sources: list[SourceSpec | dict | str], output_path: Path, fetch_html=fetch_html) -> dict:
    result = scan_sources(sources, fetch_html=fetch_html)
    write_scan_result(result, output_path)
    stage_candidates(result, output_path.with_name("discovered_candidates.json"))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Event Tracker")
    parser.add_argument("command", choices=["refresh", "status", "scan"])
    parser.add_argument("--input", type=Path, default=Path("data/verified_events.json"))
    parser.add_argument("--database", type=Path, default=Path("data/events.sqlite"))
    parser.add_argument("--output", type=Path, default=Path("data/Event_Tracker.xlsx"))
    parser.add_argument("--speaker-input", type=Path, default=None,
                        help="Optional speaker-opportunity JSON; default is paired only with data/verified_events.json")
    args = parser.parse_args()
    if args.command == "refresh":
        count = refresh_from_file(args.database, args.input, args.output, args.speaker_input)
        print(f"Refreshed the tracker from {count} event records in {args.output}")
    elif args.command == "scan":
        source_pages = json.loads(Path("config/source_pages.json").read_text(encoding="utf-8"))
        result = run_scan(source_pages, Path("data/discovered_links.json"))
        counts = result["counts"]
        staged = json.loads(Path("data/discovered_candidates.json").read_text(encoding="utf-8"))
        blocked_sources = sum(source["outcome"] == "BLOCKED" for source in result["sources"])
        print(f"Scanned {counts['sources']} registered sources, fetched {counts['pages_fetched']} pages; "
              f"found {counts['candidate_links']} raw links / {counts['unique_candidates']} unique links; "
              f"staged {len(staged)} cumulative candidates; {counts['rejected_links']} links rejected; "
              f"{blocked_sources} sources blocked; verified rows were not changed")
    else:
        store = EventStore(args.database)
        events = store.list_events()
        speakers = store.list_speaker_opportunities()
        scheduled = sum(is_scheduled(event) for event in events)
        print(f"{len(events)} event records: {scheduled} on the schedule, {len(events)-scheduled} pending; "
              f"{len(speakers)} speaker opportunities")


if __name__ == "__main__":
    main()
