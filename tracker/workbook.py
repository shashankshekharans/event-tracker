"""Build the Excel tracker and import its editable shortlist marks."""

import json
import os
from pathlib import Path

from openpyxl import Workbook, load_workbook

from tracker.event_status import is_scheduled
from tracker.workbook_views import (
    LEADERSHIP_SHEET, PENDING_SHEET, add_leadership_sheet, add_navigation,
    add_pending_sheet, excel_date, format_table,
)

COLUMNS = [
    "Event ID", "Shortlist", "Event", "City", "Region", "Start date", "End date",
    "Venue", "Organizer", "Edition", "Event type", "Industry", "Business model",
    "Suitability", "Suitability reason", "Exhibitors", "Footfall", "Footfall period",
    "Booking deadline", "Participation options", "Source URL", "Corroborating source URL",
    "Date certainty", "Last checked", "Missing information", "Speaker status",
    "Evidence status", "Audit note", "Possible duplicate key",
]

DETAIL_FIELDS = (
    "venue", "organizer", "edition", "event_type", "industry", "business_model",
    "suitability", "suitability_reason", "exhibitors", "footfall", "footfall_period",
    "booking_deadline", "participation",
)


def _load_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _add_events(workbook, events, speaker_status):
    sheet = workbook.active
    sheet.title = "Events"
    sheet.append(COLUMNS)
    for event in events:
        details = event["details"]
        evidence = details.get("audit_status", "Previously recorded")
        sheet.append([
            event["event_id"], "Yes" if event["shortlisted"] else "No", event["name"], event["city"],
            details.get("region"), excel_date(event["start_date"]), excel_date(event["end_date"]),
            *(details.get(field) for field in DETAIL_FIELDS), event["source_url"],
            details.get("source_crosscheck_url"), details.get("date_certainty") or "SOURCE DATE ON FILE",
            excel_date(details.get("last_checked")), details.get("missing_information"),
            speaker_status.get(event["event_id"], "UNKNOWN"), evidence, details.get("audit_note"),
            details.get("possible_duplicate"),
        ])
    format_table(sheet, "EventSchedule",
                 [22, 12, 39, 20, 19, 18, 18, 33, 29, 13, 23, 30, 22, 16, 45, 22, 18,
                  20, 19, 27, 32, 32, 31, 19, 45, 19, 24, 49, 32],
                 freeze="D2", hidden=(1,), links=(21, 22), shortlist=True)


def _add_speakers(workbook, opportunities, events_by_id):
    sheet = workbook.create_sheet("Speaker Opportunities")
    sheet.append(["Opportunity ID", "Shortlist", "Event ID", "Event", "City", "Event start",
                  "Event end", "Status", "Session type", "Topic", "Eligibility", "Deadline",
                  "Application URL", "Contact", "Evidence URL", "Last checked", "Missing information", "Event date evidence"])
    for item in opportunities:
        event = events_by_id[item["event_id"]]
        scheduled = is_scheduled(event)
        sheet.append([
            item["opportunity_id"], "Yes" if item["shortlisted"] else "No", item["event_id"],
            item["event_name"], item["event_city"], excel_date(item["event_start_date"]) if scheduled else None,
            excel_date(item["event_end_date"]) if scheduled else None, item["status"], item["session_type"], item["topic"],
            item["eligibility"], excel_date(item["deadline"]), item["application_url"], item["contact"],
            item["evidence_url"], excel_date(item["last_checked"]), item["missing_information"],
            event["details"].get("audit_status") or ("Previously recorded" if scheduled else "Date pending"),
        ])
    format_table(sheet, "SpeakerLeads", [25, 12, 25, 42, 20, 18, 18, 17, 30, 44, 36, 18, 32, 32, 32, 18, 59, 26],
                 freeze="E2", hidden=(1, 3), links=(13, 15), shortlist=True)


def _add_source_health(workbook, events):
    sheet = workbook.create_sheet("Source Health")
    sheet.append(["Source ID", "Publisher", "Source URL", "Outcome", "Pages fetched", "Permission",
                  "Last checked", "Notes"])
    report = _load_json(Path("data/discovered_links.json"), {})
    registry = {item["id"]: item for item in _load_json(Path("config/source_pages.json"), [])
                if isinstance(item, dict) and item.get("id")}
    scanned = {row["source_id"]: row for row in report.get("sources", []) if row.get("source_id")}
    for key, result in sorted(scanned.items()):
        source = registry.get(key, {})
        reason = result.get("permission_reason") or source.get("permission_reason")
        notes = " | ".join(dict.fromkeys(filter(None, [result.get("error"), reason])))
        sheet.append([key, result.get("publisher") or source.get("publisher"), result.get("url"),
                      result.get("outcome", "UNKNOWN"), result.get("pages_fetched", 0),
                      source.get("permitted_use") or result.get("permitted_use"),
                      result.get("checked_at"), notes])
    evidence_urls = {url for event in events for url in (
        event["source_url"], event["details"].get("source_crosscheck_url"), event["details"].get("prior_url")
    ) if url}
    for url in sorted(evidence_urls - {item.get("url") for item in scanned.values()}):
        sheet.append(["event-evidence", "Event evidence", url, "NO CRAWL LOG", 0, None, None,
                      "See the event's evidence status to determine whether its date has been checked."])
    format_table(sheet, "SourceChecks", [25, 34, 42, 25, 15, 18, 33, 59], links=(3,), color="597183")


def _add_dictionary(workbook):
    sheet = workbook.create_sheet("Data Dictionary")
    sheet.append(["Field or label", "Meaning"])
    for name, meaning in [
        ("Shortlist", "Choose Yes or No. Events and Dates Pending use the same event mark when an edition moves between sheets."),
        ("Speaker shortlist", "A Yes or No mark for each speaking route, independent of the event mark."),
        ("Leadership shortlist", "A Yes or No mark for each award, CEO talk or competition lead carried forward from the workbook."),
        ("Organizer date checked", "A current primary source shows the edition dates. Other details may still require confirmation."),
        ("Previously recorded", "A dated entry from the original tracker with the source link on file. Its dates were carried forward in this audit."),
        ("Evidence pending", "The supplied edition, date or venue lacks adequate supporting evidence in this audit."),
        ("Planning window only", "A month or broad period based on sourced prior timing or an organizer announcement. Recheck before booking."),
        ("Previously supplied date", "The original date retained for audit reference. Use the review note and evidence status when deciding what to do."),
        ("Possible duplicate key", "A same-city, same-year name match flagged for manual review. Co-located shows may be distinct."),
        ("UNKNOWN speaker status", "Confirm the edition, submission window, selection process or sponsorship terms with the organizer."),
        ("Source Health", "Crawler request history. Consult the event record for evidence on the specific date."),
    ]:
        sheet.append([name, meaning])
    format_table(sheet, "TrackerDefinitions", [29, 90], color="597183")


def export_workbook(store, output_path, leadership_records=()):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    marks = {}
    if output_path.exists():
        marks = _read_marks(output_path, (LEADERSHIP_SHEET,))
    workbook = Workbook()
    events = store.list_events()
    scheduled = sorted((event for event in events if is_scheduled(event)),
                       key=lambda event: (event["start_date"], event["city"], event["name"]))
    pending = sorted((event for event in events if not is_scheduled(event)),
                     key=lambda event: (event["details"].get("region") != "Delhi NCR", event["name"]))
    speakers = store.list_speaker_opportunities()
    _add_events(workbook, scheduled, store.speaker_status_by_event(speakers))
    add_pending_sheet(workbook, pending)
    _add_speakers(workbook, speakers, {event["event_id"]: event for event in events})
    add_leadership_sheet(workbook, leadership_records, marks)
    _add_source_health(workbook, events)
    _add_dictionary(workbook)
    add_navigation(workbook, {"Events": len(scheduled), PENDING_SHEET: len(pending),
                              "Speaker Opportunities": len(speakers), LEADERSHIP_SHEET: len(leadership_records)})
    temporary_path = output_path.with_suffix(".new.xlsx")
    try:
        workbook.save(temporary_path)
        os.replace(temporary_path, output_path)
    finally:
        workbook.close()
        temporary_path.unlink(missing_ok=True)


def _read_marks(workbook_path, sheet_names):
    workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        marks = {}
        for name in sheet_names:
            if name not in workbook.sheetnames:
                continue
            for key, mark in workbook[name].iter_rows(min_row=2, max_col=2, values_only=True):
                if key is None and mark is None:
                    continue
                if not key or mark not in ("Yes", "No"):
                    raise ValueError(f"Invalid shortlist value in {name} for {key}: {mark}")
                if key in marks and marks[key] != mark:
                    raise ValueError(f"Conflicting shortlist values for {key}")
                marks[key] = mark
        return marks
    finally:
        workbook.close()


def import_shortlist(store, workbook_path):
    known = {event["event_id"] for event in store.list_events()}
    marks = _read_marks(workbook_path, ("Events", PENDING_SHEET))
    unknown = marks.keys() - known
    if unknown:
        raise ValueError(f"Unknown event ID in workbook: {sorted(unknown)[0]}")
    for key, mark in marks.items():
        store.set_shortlist(key, mark == "Yes")


def import_speaker_shortlist(store, workbook_path):
    known = {item["opportunity_id"] for item in store.list_speaker_opportunities()}
    for key, mark in _read_marks(workbook_path, ("Speaker Opportunities",)).items():
        if key in known:
            store.set_speaker_shortlist(key, mark == "Yes")
