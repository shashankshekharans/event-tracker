"""Reviewable staging records for event-like links found by public crawls."""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def stage_candidates(scan_result: dict, output_path: Path) -> list[dict]:
    existing = []
    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))
    by_id = {item.get("candidate_id") or hashlib.sha256(item.get("url", "").encode()).hexdigest()[:16]: item for item in existing if item.get("url")}
    fetched_at = scan_result.get("generated_at", datetime.now(timezone.utc).isoformat())
    for item in scan_result.get("candidates", []):
        url = item["url"]
        identity = url + ("#" + item.get("label", "") if item.get("source_type") else "")
        candidate_id = hashlib.sha256(identity.encode()).hexdigest()[:16]
        previous = by_id.get(candidate_id, {})
        source_ids = sorted(set(previous.get("discovery_source_ids", [])) | set(item.get("discovered_from", [])))
        by_id[candidate_id] = {
            "candidate_id": candidate_id,
            "title": item.get("label", "").strip() or url.rsplit("/", 1)[-1],
            "url": url,
            "candidate_type": item.get("source_type", "event_page_link"),
            "discovery_source_ids": source_ids,
            "observed_date_city_text": item.get("observed_date_city_text", previous.get("observed_date_city_text", "")),
            "retrieved_at": fetched_at,
            "verification_status": previous.get("verification_status", "UNVERIFIED"),
            "possible_year": (re.search(r"20(?:26|27)", url + " " + item.get("label", "")) or [""])[0],
        }
    output = sorted(by_id.values(), key=lambda item: (item.get("possible_year", ""), item.get("title", "").casefold(), item["url"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    return output
