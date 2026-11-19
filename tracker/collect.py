"""Permission-aware, low-volume discovery of public event listings."""

from __future__ import annotations

import hashlib
import json
import re
import time
import base64
from dataclasses import dataclass
from io import BytesIO
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urldefrag, urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup
import requests


EVENT_TERMS = re.compile(
    r"\b(expo|exhibition|fair|summit|conclave|conference|congress|trade\s?show|"
    r"convention|show|event|book\s?fair)\b",
    re.I,
)
DATED_EVENT_CONTEXT = re.compile(
    r"\b(?:(?:\d{1,2}\s*(?:-|–|to)\s*\d{1,2})\s+"
    r"(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"|(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
    r"jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
    r"\s+\d{1,2}\s*(?:-|–|to)\s*\d{1,2})[\s,–-]{0,30}20(?:26|27)\b",
    re.I,
)
DETAIL_EVENT_PATH = re.compile(r"/calendar_event/|/(?:event|expo|exhibition|fair|show|summit|conference)[-_a-z0-9./]*20(?:26|27)[-_a-z0-9./]*$", re.I)
REJECT_TERMS = re.compile(
    r"privacy|cookie|terms|contact|about|login|sign.?in|register|registration|"
    r"enquire|enquiry|exhibit.?now|advertis|gallery|photo|video|facebook|"
    r"instagram|linkedin|youtube|twitter|sitemap|career|newsletter|blog|"
    r"press.?release|cookie|policy|javascript|catalog(?:ue)?|preview|floor.?plan|brochure|download",
    re.I,
)
ALLOWED_EVENT_PATH = re.compile(
    r"/(event|events|expo|expos|exhibition|exhibitions|fair|fairs|show|shows|"
    r"calendar|calendar_event|bookfair|bookfairs|summit|conference|congress)(/|[-_0-9]|$)",
    re.I,
)
BLOCKED_EXTENSIONS = re.compile(r"\.(?:jpe?g|png|gif|webp|svg|mp4|mov|zip|docx?|xlsx?|pptx?|pdf)$", re.I)
TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}
BLOCKED_HOSTS = {"facebook.com", "instagram.com", "linkedin.com", "youtube.com", "youtu.be", "x.com", "twitter.com", "docs.google.com", "accounts.google.com"}
HTTP = requests.Session()
HTTP.headers.update({"User-Agent": "AAJEventResearch/0.2 (local public event research)"})


class CrawlBlockedError(ValueError):
    """The requested page attempts to leave the approved source origin."""


@dataclass(frozen=True)
class SourceSpec:
    id: str
    url: str
    publisher: str
    source_layer: str
    enabled: bool
    permitted_use: str
    permission_reason: str
    terms_url: str = ""
    robots_review: str = ""
    request_delay_seconds: float = 2.0
    max_pages: int = 20
    max_depth: int = 1
    content_type: str = "html"
    scope: str = ""
    reviewed_at: str = ""


def source_spec(value: SourceSpec | dict | str) -> SourceSpec:
    """Normalize a source record; legacy strings are disabled by default."""
    if isinstance(value, SourceSpec):
        return value
    if isinstance(value, str):
        return SourceSpec(
            id=hashlib.sha1(value.encode()).hexdigest()[:10], url=value,
            publisher=urlsplit(value).netloc, source_layer="unreviewed",
            enabled=False, permitted_use="REVIEW_REQUIRED",
            permission_reason="Legacy URL has no recorded terms/robots review.",
        )
    return SourceSpec(**{field: value.get(field, default) for field, default in {
        "id": "", "url": "", "publisher": "", "source_layer": "",
        "enabled": False, "permitted_use": "REVIEW_REQUIRED", "permission_reason": "",
        "terms_url": "", "robots_review": "", "request_delay_seconds": 2.0,
        "max_pages": 20, "max_depth": 1, "content_type": "html", "scope": "", "reviewed_at": "",
    }.items()})


def canonicalize_url(url: str) -> str:
    url, _ = urldefrag(url.strip())
    parts = urlsplit(url)
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if k.lower() not in TRACKING_PARAMS]
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), ""))


def _host_allowed(candidate: str, base: str) -> bool:
    host = (urlsplit(candidate).hostname or "").lower()
    base_host = (urlsplit(base).hostname or "").lower()
    if host in BLOCKED_HOSTS or any(host.endswith("." + blocked) for blocked in BLOCKED_HOSTS):
        return False
    return host.removeprefix("www.") == base_host.removeprefix("www.")


def _rejection_reason(url: str, label: str, base_url: str) -> str | None:
    path = urlsplit(url).path
    if not _host_allowed(url, base_url):
        return "external_or_social_domain"
    if BLOCKED_EXTENSIONS.search(path):
        return "non_html_asset"
    if REJECT_TERMS.search(label):
        return "navigation_or_action_link"
    if not ALLOWED_EVENT_PATH.search(path) and not EVENT_TERMS.search(label) and not DETAIL_EVENT_PATH.search(path):
        return "no_event_signal"
    if REJECT_TERMS.search(path):
        return "navigation_or_action_path"
    return None


def discover_event_links(base_url: str, html: str) -> tuple[list[dict], list[dict]]:
    """Extract candidate event links and explicit rejected-link reasons."""
    soup = BeautifulSoup(html, "html.parser")
    candidates: dict[str, dict] = {}
    rejected: list[dict] = []

    def structured_events(value):
        if isinstance(value, list):
            for child in value:
                yield from structured_events(child)
        elif isinstance(value, dict):
            types = value.get("@type", [])
            if isinstance(types, str):
                types = [types]
            if any(str(item).casefold().endswith("event") for item in types):
                yield value
            for key, child in value.items():
                if key in ("@graph", "mainEntity", "itemListElement"):
                    yield from structured_events(child)

    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError):
            continue
        for event in structured_events(payload):
            raw_url = event.get("url") or event.get("@id")
            if isinstance(raw_url, dict):
                raw_url = raw_url.get("@id")
            if not isinstance(raw_url, str) or not raw_url.strip():
                continue
            url = canonicalize_url(urljoin(base_url, raw_url))
            label = str(event.get("name") or "Structured event")
            if not EVENT_TERMS.search(label):
                label = f"{label} event"
            if not _host_allowed(url, base_url):
                rejected.append({"url": url, "label": label, "reason": "external_or_social_domain"})
                continue
            location = event.get("location") or {}
            if isinstance(location, list):
                location = location[0] if location else {}
            address = location.get("address", {}) if isinstance(location, dict) else {}
            if isinstance(address, dict):
                city = address.get("addressLocality", "")
            else:
                city = str(address)
            candidates.setdefault(url, {
                "url": url, "label": label, "discovered_from": base_url,
                "observed_date_city_text": " | ".join(filter(None, [
                    str(event.get("startDate", "")), city,
                    str(location.get("name", "")) if isinstance(location, dict) else "",
                ])),
                "structured_event": True,
            })

    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "").strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        url = canonicalize_url(urljoin(base_url, href))
        label = anchor.get_text(" ", strip=True)
        context = anchor.parent.get_text(" ", strip=True) if anchor.parent else label
        if (urlsplit(base_url).hostname or "").removeprefix("www.") == "ficci.in":
            path = urlsplit(url).path
            if path.startswith("/event/") and label.casefold() == "add to calendar":
                continue
            if path.startswith("/event-details/"):
                card = anchor.find_parent(class_="single-list")
                title = card.find("h3") if card else None
                if title is None:
                    continue
                label = title.get_text(" ", strip=True)
                context = card.get_text(" ", strip=True)
        context = re.sub(r"\s+", " ", context).strip()[:500]
        dated_event_context = DATED_EVENT_CONTEXT.search(context)
        reason = _rejection_reason(url, label, base_url)
        if reason == "no_event_signal" and dated_event_context:
            reason = None
        if reason:
            if EVENT_TERMS.search(label + " " + url) or DETAIL_EVENT_PATH.search(urlsplit(url).path):
                rejected.append({"url": url, "label": label, "reason": reason})
            continue
        if REJECT_TERMS.search(label + " " + url):
            continue
        if (not EVENT_TERMS.search(label + " " + url)
                and not DETAIL_EVENT_PATH.search(urlsplit(url).path)
                and not dated_event_context):
            continue
        if dated_event_context and (not EVENT_TERMS.search(label) or label.casefold() in {"explore now", "read more"}):
            label = f"Dated event listing — {context}"[:180]
        candidates.setdefault(url, {"url": url, "label": label, "discovered_from": base_url,
                                    "observed_date_city_text": context})
    return sorted(candidates.values(), key=lambda item: item["url"]), rejected


def _fetch_bytes(url: str, timeout=(5, 20)) -> tuple[bytes, str]:
    cache_dir = Path("data/http_cache")
    cache_path = cache_dir / (hashlib.sha256(canonicalize_url(url).encode()).hexdigest() + ".json")
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text(encoding="utf-8"))
            if time.time() - cached["saved_at"] < 86400:
                return base64.b64decode(cached["content"]), cached["content_type"]
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            pass
    original = url
    current = url
    response = None
    for redirect in range(6):
        response = HTTP.get(current, timeout=timeout, allow_redirects=False)
        if response.is_redirect or response.is_permanent_redirect:
            location = response.headers.get("Location")
            if not location or redirect == 5:
                raise CrawlBlockedError(f"Invalid or excessive redirect chain: {url}")
            target = urljoin(current, location)
            if not _host_allowed(target, original) or (urlsplit(original).scheme == "https" and urlsplit(target).scheme != "https"):
                raise CrawlBlockedError(f"Redirect leaves the reviewed source origin: {current} -> {target}")
            current = target
            continue
        if 500 <= response.status_code < 600:
            time.sleep(0.8)
            response = HTTP.get(current, timeout=timeout, allow_redirects=False)
            if response.is_redirect or response.is_permanent_redirect:
                raise ValueError(f"Redirect after server-error retry requires a fresh policy check: {current}")
        response.raise_for_status()
        break
    content_type = response.headers.get("Content-Type", "").lower()
    content = response.content
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps({"saved_at": time.time(), "content_type": content_type,
                                      "content": base64.b64encode(content).decode("ascii")}), encoding="utf-8")
    return content, content_type


def _has_fresh_cache(url: str) -> bool:
    cache_path = Path("data/http_cache") / (hashlib.sha256(canonicalize_url(url).encode()).hexdigest() + ".json")
    if not cache_path.exists():
        return False
    try:
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        return time.time() - cached["saved_at"] < 86400
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return False


def fetch_html(url: str) -> str:
    content, content_type = _fetch_bytes(url)
    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
        raise ValueError(f"Unsupported content type: {content_type or 'unknown'}")
    return content.decode("utf-8", errors="replace")


def fetch_pdf_text(url: str) -> str:
    """Read text from a publicly reachable PDF; no OCR or access-control bypass."""
    from pypdf import PdfReader
    content, content_type = _fetch_bytes(url, timeout=(5, 30))
    if "application/pdf" not in content_type and not url.lower().endswith(".pdf"):
        raise ValueError("Configured PDF source did not return a PDF")
    return "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)


def _pdf_candidates(source: SourceSpec, text: str) -> list[dict]:
    candidates = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip(" |\t-")
        if len(line) < 8 or len(line) > 500 or not EVENT_TERMS.search(line):
            continue
        if not re.search(r"20(?:26|27)", line):
            continue
        candidates.append({"url": source.url, "label": line, "discovered_from": source.url,
                           "observed_date_city_text": line, "source_type": "government_calendar_pdf"})
    return candidates


def scan_source(source: SourceSpec, fetch_page=fetch_html, sleep=time.sleep) -> dict:
    checked_at = datetime.now(timezone.utc).isoformat()
    result = {"source_id": source.id, "url": source.url, "publisher": source.publisher,
              "source_layer": source.source_layer, "scope": source.scope,
              "enabled": source.enabled, "permitted_use": source.permitted_use,
              "permission_reason": source.permission_reason, "terms_url": source.terms_url,
              "reviewed_at": source.reviewed_at, "robots_review": source.robots_review,
              "outcome": "", "checked_at": checked_at, "pages_fetched": 0,
              "candidates": [], "rejected_links": [], "error": ""}
    if not source.enabled or source.permitted_use != "ALLOW":
        result["outcome"] = "BLOCKED"
        result["error"] = source.permission_reason or "Source is not explicitly enabled for permitted use."
        return result

    if source.content_type == "pdf":
        try:
            text = fetch_pdf_text(source.url)
            result["pages_fetched"] = 1
            result["candidates"] = _pdf_candidates(source, text)
            result["outcome"] = "SUCCESS_WITH_EVENTS" if result["candidates"] else "SUCCESS_EMPTY"
            snapshot = Path("data/source_snapshots") / f"{source.id}.txt"
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_text(text, encoding="utf-8")
        except CrawlBlockedError as error:
            result["outcome"] = "BLOCKED"
            result["error"] = str(error)
        except requests.HTTPError as error:
            code = getattr(error.response, "status_code", None)
            result["outcome"] = "BLOCKED" if code in (401, 403, 429) else "FAILED"
            result["error"] = f"HTTP {code}: {source.url}"
        except Exception as error:
            result["outcome"] = "FAILED"
            result["error"] = str(error)
        return result

    seen_pages: set[str] = set()
    queue = [(canonicalize_url(source.url), 0)]
    candidates: dict[str, dict] = {}
    rejected: list[dict] = []
    failures = 0
    blocked = False
    uncached_requests = 0
    while queue and result["pages_fetched"] < max(1, source.max_pages):
        page_url, depth = queue.pop(0)
        if page_url in seen_pages:
            continue
        seen_pages.add(page_url)
        cache_hit = fetch_page is fetch_html and _has_fresh_cache(page_url)
        if not cache_hit:
            if uncached_requests:
                sleep(max(0.0, source.request_delay_seconds))
            uncached_requests += 1
        try:
            html = fetch_page(page_url)
            result["pages_fetched"] += 1
            links, rejected_links = discover_event_links(page_url, html)
            rejected.extend(rejected_links)
            for link in links:
                candidates.setdefault(link["url"], link)
                if depth < source.max_depth and len(seen_pages) + len(queue) < source.max_pages:
                    queue.append((link["url"], depth + 1))
        except requests.HTTPError as error:
            failures += 1
            status = getattr(error.response, "status_code", None)
            if status in (401, 403, 404, 410, 429):
                result["error"] = f"HTTP {status}: {page_url}"
            if status in (401, 403, 429):
                blocked = True
                break
            else:
                result["error"] = str(error)
        except CrawlBlockedError as error:
            failures += 1
            blocked = True
            result["error"] = str(error)
            break
        except (requests.RequestException, ValueError) as error:
            failures += 1
            result["error"] = str(error)
    result["candidates"] = sorted(candidates.values(), key=lambda item: item["url"])
    result["rejected_links"] = sorted({(x["url"], x["reason"]): x for x in rejected}.values(), key=lambda x: x["url"])
    if blocked:
        result["outcome"] = "BLOCKED"
    elif failures and result["candidates"]:
        result["outcome"] = "PARTIAL"
    elif failures:
        result["outcome"] = "FAILED"
    elif result["candidates"]:
        result["outcome"] = "SUCCESS_WITH_EVENTS"
    else:
        result["outcome"] = "SUCCESS_EMPTY"
    return result


def scan_sources(sources: list[SourceSpec | dict | str], fetch_html=fetch_html, sleep=time.sleep) -> dict:
    """Run sources sequentially; unreviewed legacy URLs never make requests."""
    source_results = [scan_source(source_spec(source), fetch_page=fetch_html, sleep=sleep)
                      for source in sources]
    all_candidates: dict[str, dict] = {}
    for result in source_results:
        for candidate in result["candidates"]:
            identity = candidate["url"] + ("#" + candidate.get("label", "") if candidate.get("source_type") else "")
            stored = all_candidates.setdefault(identity, dict(candidate, discovered_from=[]))
            if result["source_id"] not in stored["discovered_from"]:
                stored["discovered_from"].append(result["source_id"])
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": source_results,
        "candidate_links": sorted(all_candidates),
        "candidates": sorted(all_candidates.values(), key=lambda item: item["url"]),
        "counts": {
            "sources": len(source_results),
            "pages_fetched": sum(item["pages_fetched"] for item in source_results),
            "candidate_links": sum(len(item["candidates"]) for item in source_results),
            "unique_candidates": len(all_candidates),
            "rejected_links": sum(len(item["rejected_links"]) for item in source_results),
        },
    }


def write_scan_result(result: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
