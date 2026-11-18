"""Manual Claude/ChatGPT batch exchange with evidence revision checks."""

import hashlib
import json
from pathlib import Path

from tracker.store import EventStore


def evidence_fingerprint(event: dict) -> str:
    evidence = {name: event[name] for name in (
        "event_id", "name", "city", "start_date", "end_date", "source_url"
    )}
    evidence["details"] = {
        key: value for key, value in event["details"].items()
        if key not in {"suitability", "ai_reason"}
    }
    encoded = json.dumps(evidence, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def export_batch(store: EventStore, output_path: Path) -> dict:
    candidates = []
    for event in store.list_events():
        candidates.append({
            "event_id": event["event_id"],
            "evidence_fingerprint": evidence_fingerprint(event),
            "name": event["name"], "city": event["city"],
            "start_date": event["start_date"], "end_date": event["end_date"],
            "source_url": event["source_url"], "details": event["details"],
        })
    payload = {
        "instructions": "Assess AAJ product suitability from the supplied source evidence. Return JSON with results containing event_id, evidence_fingerprint, suitability (GREEN, AMBER, RED, UNKNOWN), and reason. Preserve uncertainty. AAJ excludes leather, perishable food, temperature-controlled, alcohol, and meat-based products. Mixed events may contain eligible product lines. Do not invent exhibitor names or metrics.",
        "candidates": candidates,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def import_batch(store: EventStore, input_path: Path) -> dict:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    current = {event["event_id"]: event for event in store.list_events()}
    report = {"accepted": [], "stale": [], "invalid": []}
    for result in payload.get("results", []):
        event_id = result.get("event_id")
        event = current.get(event_id)
        if event is None or result.get("suitability") not in {"GREEN", "AMBER", "RED", "UNKNOWN"} or not result.get("reason"):
            report["invalid"].append(event_id)
            continue
        if result.get("evidence_fingerprint") != evidence_fingerprint(event):
            report["stale"].append(event_id)
            continue
        store.update_assessment(event_id, result["suitability"], result["reason"])
        report["accepted"].append(event_id)
    return report
