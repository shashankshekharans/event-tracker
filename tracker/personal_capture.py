"""Capture unverified event leads from directory pages opened by the user locally."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from tracker.collect import canonicalize_url


LOCAL_ROOT = Path("data/personal_capture")
MONTH = r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
DATE_HINT = re.compile(
    rf"\b(?:\d{{1,2}}\s*[-–]\s*\d{{1,2}}\s+)?(?:{MONTH})\s+\d{{1,2}}[\s,/-]*20(?:26|27)\b"
    rf"|\b\d{{1,2}}(?:\s*[-–]\s*\d{{1,2}})?\s+(?:{MONTH})[\s,]*20(?:26|27)\b"
    r"|\b20(?:26|27)-\d{2}-\d{2}\b",
    re.I,
)
ACTION_LABEL = re.compile(r"^(?:more events?|view all|see all|sign.?in|log.?in|register|interested|follow|share|next|previous|home)$", re.I)


def _site_host(site: str) -> str:
    return {"10times": "10times.com", "whr": "whr.ai"}[site]


def _host_matches(host: str, expected: str) -> bool:
    return host == expected or host.endswith("." + expected)


def extract_leads(html: str, page_url: str, site: str) -> list[dict]:
    """Extract dated, event-like links from one rendered page without promoting them."""
    expected = _site_host(site)
    if not _host_matches((urlsplit(page_url).hostname or "").lower(), expected):
        raise ValueError(f"Page URL must be on {expected}")
    soup = BeautifulSoup(html, "html.parser")
    leads = {}
    for anchor in soup.select("a[href]"):
        title = " ".join(anchor.get_text(" ", strip=True).split())
        if len(title) < 8 or ACTION_LABEL.fullmatch(title):
            continue
        url = canonicalize_url(urljoin(page_url, anchor["href"]))
        host = (urlsplit(url).hostname or "").lower()
        path = urlsplit(url).path.lower()
        if not _host_matches(host, expected) or url == canonicalize_url(page_url):
            continue
        if any(term in path for term in ("/signin", "/login", "/register", "/privacy", "/terms")):
            continue
        context = ""
        for parent in list(anchor.parents)[:5]:
            text = " ".join(parent.get_text(" ", strip=True).split())
            if len(text) <= 700 and DATE_HINT.search(text):
                context = text
                break
        if not context:
            continue
        leads.setdefault(url, {"source_site": site, "title": title, "url": url,
                               "observed_text": context[:500], "page_url": page_url,
                               "verification_status": "UNVERIFIED"})
    return sorted(leads.values(), key=lambda item: (item["title"].casefold(), item["url"]))


def save_leads(path: Path, leads: list[dict]) -> int:
    """Merge local leads by URL and return the number of new records."""
    existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    by_url = {item["url"]: item for item in existing}
    added = 0
    for item in leads:
        if item["url"] in by_url:
            continue
        by_url[item["url"]] = dict(item, captured_at=datetime.now(timezone.utc).isoformat())
        added += 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(by_url.values(), key=lambda item: item["url"]),
                               indent=2, ensure_ascii=False), encoding="utf-8")
    return added


def _capture_browser(site: str, url: str, channel: str, limit: int, output: Path) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise SystemExit("Install the optional browser dependency: python -m pip install -r requirements-personal.txt") from exc

    profile = LOCAL_ROOT / "browser-profile" / site
    profile.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            str(profile.resolve()), channel=channel, headless=False)
        try:
            page = context.pages[0] if context.pages else context.new_page()
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
            except Exception as exc:
                print(f"Initial page navigation did not complete: {exc}")
            for _ in range(limit):
                choice = input("Open a listing page in the browser, then press Enter to capture it (q to quit): ").strip().lower()
                if choice == "q":
                    break
                page = context.pages[-1]
                leads = extract_leads(page.content(), page.url, site)
                if not leads:
                    print("No dated event links found. Check that a listing page is visible, then try again.")
                    continue
                added = save_leads(output, leads)
                print(f"Found {len(leads)} links; added {added} local unverified leads to {output}.")
        finally:
            context.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture personal, unverified directory leads locally")
    parser.add_argument("--site", choices=("10times", "whr"), required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url", help="Public listing URL to open in a visible browser")
    source.add_argument("--html-file", type=Path, help="Locally saved HTML listing for offline extraction")
    parser.add_argument("--page-url", help="Original URL of --html-file")
    parser.add_argument("--channel", choices=("chrome", "msedge"), default="chrome")
    parser.add_argument("--max-pages", type=int, default=10)
    args = parser.parse_args()
    if args.max_pages < 1 or args.max_pages > 50:
        parser.error("--max-pages must be between 1 and 50")
    output = LOCAL_ROOT / f"{args.site}_leads.json"
    if args.html_file:
        if not args.page_url:
            parser.error("--page-url is required with --html-file")
        leads = extract_leads(args.html_file.read_text(encoding="utf-8"), args.page_url, args.site)
        added = save_leads(output, leads)
        print(f"Found {len(leads)} links; added {added} local unverified leads to {output}.")
    else:
        if not _host_matches((urlsplit(args.url).hostname or "").lower(), _site_host(args.site)):
            parser.error("--url must match the selected site")
        _capture_browser(args.site, args.url, args.channel, args.max_pages, output)


if __name__ == "__main__":
    main()
