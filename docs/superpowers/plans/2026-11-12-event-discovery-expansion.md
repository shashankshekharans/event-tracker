# Permission-Aware Event Discovery Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the deduplicated event-edition pool toward 200+ India events through December 2027 using free, permitted Python collection and a source-backed candidate-to-verified workflow.

**Architecture:** Replace the URL-only registry with explicit source records that include permission state and crawl policy. The Python requests/BeautifulSoup collector will fetch only enabled public pages, extract event-like links, deduplicate candidates, and save a reviewable staging file. Event facts are verified from organizer/venue evidence before becoming confirmed workbook rows.

**Tech Stack:** Python 3.12, requests, BeautifulSoup, SQLite, JSON, openpyxl; no paid APIs, search services, or hosting.

**Spec:** [Event Discovery and Speaker Opportunities design](../specs/2026-11-12-event-discovery-and-speaker-opportunities-design.md)

## Global Constraints

- Keep the workflow free and local-first.
- Do not crawl 10times, import its directory content, or bypass its access controls unless written permission for AAJ's use is obtained.
- Do not enable paid WHR.ai services or APIs in this phase.
- Review source terms/robots and intended internal use before enabling any directory.
- Preserve the NCR-first geography and retain other metros and Tier 2 locations.
- Do not pad the 200+ target with duplicates, stale editions, invented dates, or unverified claims.
- Keep candidates distinct from verified event editions; carry uncertainty and provenance visibly.

## Review Focus

1. A source is disallowed or its permission status is unknown — it must remain disabled and produce no requests.
2. A source page has hundreds of navigation links or media assets — only relevant public event links become candidates.
3. A 2027 event has tentative, conflicting, or missing dates — preserve uncertainty; do not count it as a confirmed dated edition.
4. The same event is listed by multiple sources or aliases — retain one edition identity with all source references.
5. Network errors or a zero-result scan occur — report failure separately from a successful empty source and preserve prior records.

## Scope Split

Speaker-opportunity persistence and workbook presentation are independent of source discovery and have their own plan: [Speaker Opportunities implementation plan](2026-11-12-speaker-opportunities.md). Event discovery should preserve speaker-call links and relevant conference pages for that plan.

## Tasks

### Task 1 — Permission-aware source registry

**Files:** Modify `config/source_pages.json`, `tracker/collect.py`, `README.md`.

- [ ] Define a source record with stable ID, URL, publisher, source layer, city/vertical scope, enabled flag, terms/robots review date, permitted-use decision, reason, request delay, and crawl depth.
- [ ] Mark 10times excluded with its explicit terms-based reason; mark WHR.ai excluded because the current free phase cannot use its paid service.
- [ ] Require an explicit `enabled=true` and `permitted_use=ALLOW` before a page is fetched.
- [ ] Record disabled-source decisions in the scan output without making a request to those domains.
- [ ] Document how to review and enable a new public directory source.

**Execution note (2026-11-12):** The current registry and policy-gated scan are implemented. The source-review procedure is documented in the README. Directory sources with explicit prohibitions or unresolved reuse terms remain disabled.

**Manual verification:** Inspect the serialized registry and scan report. Confirm no request record is emitted for disabled/disallowed sources.

### Task 2 — Relevant event-link extraction and safe crawl limits

**Files:** Modify `tracker/collect.py`, `tracker/cli.py`, `data/discovered_links.json`.

- [ ] Keep the public interface `scan_sources(sources: list[SourceSpec], fetch_html=fetch_html) -> dict` and output distinct source outcomes, event candidates, and errors.
- [ ] Filter links by event-related text/path plus allowed content type; reject images, registration-only pages, generic navigation, privacy pages, and unrelated external links.
- [ ] Follow same-domain event-detail links only within the source's configured depth and per-source page cap; do not submit forms, log in, or solve challenges.
- [ ] Add bounded timeouts, one low-concurrency worker, per-domain delay, retry only for transient server errors, and a local response cache keyed by URL/content hash.
- [ ] Canonicalize URLs and keep the URLs that discovered each candidate.
- [ ] Report `SUCCESS_WITH_EVENTS`, `SUCCESS_EMPTY`, `PARTIAL`, `FAILED`, or `BLOCKED` accurately.

**Execution note (2026-11-12):** Implemented sequential same-origin collection, per-source page/depth limits, a 24-hour local response cache, bounded timeouts, one retry for HTTP 5xx, guarded same-origin redirects, and explicit outcome reporting. The latest run fetched 37 pages from 20 registered sources; excluded sources reported `BLOCKED` with zero pages fetched.

**Manual verification:** Run the collector against one approved venue calendar and one approved organizer calendar; inspect a sample of included links and rejected navigation/assets, then run the registered-source batch and inspect its status summary.

### Task 3 — Candidate staging and edition deduplication

**Files:** Create `tracker/candidates.py`; modify `tracker/cli.py`; create `data/discovered_candidates.json`.

- [ ] Store candidate ID, discovered title/link, discovery source IDs, observed date/city text, retrieval time, and verification status without overwriting confirmed records.
- [ ] Merge exact canonical URLs and publisher IDs automatically; mark name/date/city near-matches as possible duplicates for review.
- [ ] Require an edition year and evidence URL before promoting a candidate into `data/verified_events.json`; allow undated announced editions only with `date_certainty=NOT ANNOUNCED`.
- [ ] Preserve conflicting observations and label tentative, estimated, or provisional dates.
- [ ] Provide a CLI report for raw links, event candidates, likely duplicates, promoted editions, and excluded links.

**Manual verification:** Import a small set containing one duplicate, one conflicting date, one undated edition, and one unrelated link; inspect their separate outcomes and source trace.

### Task 4 — Expand source coverage and pursue 200+ editions

**Files:** Modify `config/source_pages.json`, `data/verified_events.json`, `README.md`, `.superpowers/sdd/2026-11-12-event-discovery-expansion/progress.md`.

- [x] Add source candidates from listing directories, venue calendars, organizers, associations, and public government/embassy calendars; enable only sources whose access/use review allows the workflow.
- [x] Prioritize NCR and ensure searches cover all months through December 2027, followed by Mumbai, Kolkata, Bengaluru, other metros, and Tier 2 cities.
- [x] Include conferences and summits as event candidates alongside exhibitions and trade fairs.
- [x] Run source scans in bounded batches and promote only distinct, evidence-backed event editions.
- [x] Continue until at least 200 distinct event editions are verified or the report shows the remaining source/coverage limitation; never inflate counts with candidate links.
- [x] Refresh the workbook and report confirmed rows, candidates awaiting review, duplicates, city/month distribution, and source failures separately.

**Manual verification:** Reconcile the workbook count against unique event-edition keys in JSON, inspect all months/cities coverage, and spot-check source links for a sample of newly promoted events.

## Handoff

Use the existing Python CLI and local workbook. Do not implement the separate speaker sheet as part of this plan; preserve event conference/programme URLs so the speaker plan can use them.

**Audit update, 18 November 2026.** The later evidence audit revised the schedule. See the [current plan](../../../PRODUCT_PLAN.md) and [agent handoff](../../../AGENTS.md).
