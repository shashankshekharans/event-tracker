# Speaker Opportunities Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Identify and track current, evidence-backed 2027 opportunities for AAJ leadership to speak at relevant Indian events.

**Architecture:** Store multiple speaker calls per event edition in SQLite under the immutable event ID. Export a dedicated Speaker Opportunities workbook sheet and a summary status on Events. Discover opportunities from official CFPs, programme pages, and explicit organizer confirmation; keep directory listings as leads only.

**Tech Stack:** Existing Python 3.12, SQLite, JSON, and openpyxl implementation; no paid API.

**Spec:** [Event Discovery and Speaker Opportunities design](../specs/2026-11-12-event-discovery-and-speaker-opportunities-design.md)

## Global Constraints

- Keep the workflow free and local-first.
- Treat speaker availability independently from event exhibitor/attendee suitability and the event shortlist mark.
- Mark `OPEN` only with current official evidence for the edition.
- Preserve deadlines, topics, eligibility, and evidence at the event-edition and speaking-call level.
- Use initial leadership topic discovery around supply chain, logistics, warehousing, fulfilment, e-commerce operations, 3PL, and logistics technology.
- No speaker acceptance or participation is implied by discovery of an open call.

## Review Focus

1. One event has multiple tracks/calls — retain separate opportunities linked to one event ID.
2. A call is closed or past its deadline — do not show it as open.
3. A page describes prior-year speakers but no current call — keep status `UNKNOWN` or `UPCOMING`, not `OPEN`.
4. A CFP has no deadline or eligibility — preserve blanks and identify the missing fields.
5. Event facts refresh while a speaker opportunity is present — retain its event ID and do not overwrite it with event-row refresh.

## Tasks

### Task 1 — Speaker opportunity persistence

**Files:** Modify `tracker/store.py`, `tracker/cli.py`; create `tracker/speakers.py`.

- [ ] Add a `speaker_opportunities` table with opportunity ID, immutable event ID, separate shortlisted Yes/No mark, status, session type, topic, eligibility, application URL, deadline, contact, evidence URL, last checked, and missing information.
- [ ] Add typed create/update/list operations; validate status values, event references, URLs, and deadline formats.
- [ ] Provide a deterministic event-level summary status without changing the shortlist or event suitability fields.
- [ ] Preserve opportunity records across event-data refreshes.

**Execution note (2026-11-12):** SQLite persistence, status/deadline/URL/event-reference validation, event-level summary, independent shortlist, and refresh loading are implemented. The seed includes one current iDAC speaker-interest form; deadline and city/edition assignment are unknown.

**Manual verification:** Create, update, list, and refresh a sample event with two distinct speaker opportunities; inspect status summary and opportunity persistence.

### Task 2 — Evidence-based discovery handoff

**Files:** Modify `tracker/candidates.py`, `tracker/cli.py`, `README.md`.

- [ ] Add a review path for official CFP/application pages, conference programme pages, and explicit organizer confirmation.
- [ ] Store discovered speaker leads separately from confirmed current calls; keep source URL and checked date on every status.
- [ ] Flag past-year agendas and closed deadlines as non-open leads for manual recheck.
- [ ] Generate query/checklist guidance for NCR-first 2027 events and the initial AAJ leadership themes without using an AI API.

**Manual verification:** Review examples of an active CFP, prior-year-only agenda, and closed call; ensure only the active current official CFP yields `OPEN`.

### Task 3 — Workbook view and local operating instructions

**Files:** Modify `tracker/workbook.py`, `README.md`, `PRODUCT_PLAN.md`.

- [ ] Add a `Speaker Opportunities` sheet with one row per call, its own Yes/No shortlist mark, event ID/name/date/city, status, session, topic, eligibility, deadline, application link, evidence link, checked date, and missing information.
- [ ] Add an event-level speaker status column to Events while preserving the independent event and speaker shortlist marks.
- [ ] Add filters, freeze panes, readable widths, and hyperlinks to the new sheet.
- [ ] Explain how Marketing/BD can review a speaking call and pass a shortlisted opportunity to leadership for discussion.

**Execution note (2026-11-12):** The workbook now has Events and Speaker Opportunities sheets in the same file, separate Yes/No shortlist marks, event-level speaker status, links, filters, and freeze panes. The README explains the shortlist handoff. Current-call discovery beyond the iDAC seed remains outstanding.

**Manual verification:** Refresh the workbook with multiple calls for one event, confirm independent rows and links, and independently mark/unmark the event and speaker opportunity shortlist cells across a second refresh.

## Handoff

The event discovery expansion plan is separate: [Permission-Aware Event Discovery Expansion](2026-11-12-event-discovery-expansion.md). Speaker-call records can be added only after event identities and source evidence exist.
