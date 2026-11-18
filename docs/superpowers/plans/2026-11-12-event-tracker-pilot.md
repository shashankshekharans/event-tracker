# Event Tracker Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a populated, locally refreshed Excel-compatible tracker of AAJ event opportunities, with evidence, source health, and shortlist marks that survive refreshes.

**Architecture:** Python collects and validates public event evidence, stores stable event identities and source history in SQLite, and exports a filterable `.xlsx` workbook. The operator can edit the workbook's shortlist column, run a refresh, and process optional Claude/ChatGPT classification batches without API access. This plan ends after Marketing and BD can inspect real listings. The Python browser dashboard, React migration, and Cloudflare deployment have later plans.

**Tech Stack:** Python 3.11+, Scrapy, Playwright for sources that need a browser, pdfplumber, Pydantic, SQLite standard library, openpyxl, pytest. Use free local tools and installed Claude/ChatGPT subscriptions through manual batch exchange.

**Spec:** [aaj_events.md](../../../aaj_events.md)

## Global Constraints

- No additional software, hosting, search, scraping, or AI API expenditure.
- Start with Delhi NCR, Mumbai, Kolkata, and Bengaluru. Give NCR deeper coverage.
- Preserve all listed customer industries, with a modest preference for B2B and B2C e-commerce businesses.
- Confirmed warehouse exclusions are leather, perishable food, temperature-controlled products, alcohol, and meat-based products, including meat-based pet food.
- A mixed event can contain eligible opportunities. Keep AMBER and UNKNOWN visible.
- Use a weekly cadence, with manual operation first and optional scheduling later.
- Persist only a shortlist mark as user input. Preserve it across rescheduling, rebranding, and refresh.
- Include event type, edition, exhibitors, footfall, participation information, evidence, and missing-data labels when available.
- Keep the pilot local. A suitable spreadsheet viewer must be verified during setup.
- Record source outcomes and distinguish a successful empty result from failure.

## Review Focus

1. An event moves from one month to another. Its immutable edition ID and shortlist mark remain attached to the updated row. Tested in Task 2.
2. The operator edits a shortlist mark in the workbook and refreshes again. The mark survives and the workbook stays readable. Tested in Task 5.
3. A source changes layout and yields zero parsed events after previously returning events. The run reports a partial or failed source and retains the previous valid observations. Tested in Task 3.
4. A mixed expo lists eligible synthetic footwear and leather products. The event remains visible with an AMBER explanation. Tested in Task 4.
5. An AI batch result arrives after its source evidence changed. Import rejects or flags the stale result and leaves current facts intact. Tested in Task 4.

---

## File map and interfaces

The repository currently contains only the design document. The implementer creates the following focused modules, retaining the exact interface names below unless a verified dependency requires an adjustment documented in the plan.

| File | Responsibility |
| --- | --- |
| `tracker/schema.py` | Pydantic contracts for source observations, event editions, cited metrics, assessments, and workbook rows. |
| `tracker/store.py` | SQLite migrations, transactions, stable event identities, source observations, assessments, refresh runs, and shortlist marks. |
| `tracker/match.py` | Candidate matching and explicit merge decisions for editions and source records. |
| `tracker/sources.py` | Source registry loading and the outcome contract for every source run. |
| `tracker/collect.py` | Scrapy-based source fetching, document extraction, and optional Playwright route. |
| `tracker/assess.py` | Deterministic candidate tags, product suitability, and evidence-backed participation suggestions. |
| `tracker/batches.py` | AI batch export and validated, idempotent result import. |
| `tracker/workbook.py` | Workbook generation, shortlist re-import, data dictionary, and source-health sheet. |
| `tracker/cli.py` | Manual collection, batch export/import, workbook refresh, and status commands. |
| `config/sources.yaml` | Verified pilot source URLs, city coverage, fetch strategy, and enabled status. |
| `tests/` | Focused tests for behavior that protects evidence, identity, and shortlist marks. |
| `data/` | Ignored generated database, snapshots, batches, workbook backups, and output. |

`tracker/schema.py` defines `SourceObservation`, `EventCandidate`, `MetricEvidence`, `EventAssessment`, and `WorkbookRow`. Their fields use the names in the design document. `tracker/store.py` exposes `open_store(path: Path) -> EventStore`. The store exposes `save_observations(run_id, observations)`, `upsert_event(candidate) -> str`, `set_shortlist(event_id, marked)`, `get_shortlist(event_id) -> bool`, `list_events()`, and `list_source_status()`. Use typed models for inputs and outputs. The CLI calls the same interfaces as tests and future UI code.

## Task 1 — Data contract and durable store

**Files:** Create `pyproject.toml`, `tracker/__init__.py`, `tracker/schema.py`, `tracker/store.py`, `tests/test_store.py`, and `.gitignore`.

**Interfaces:** Produce the models and store API described in the file map. Task 2 consumes `upsert_event` and the shortlist methods. Tasks 3–6 consume source and event reads.

- [ ] Write failing tests for a round trip of an event, cited metric, source observation, refresh run, and shortlist mark. Assert date ordering, required AMBER/RED reason, metric provenance, and status enum validation.
- [ ] Run `python -m pytest tests/test_store.py -q` and confirm the new tests fail for missing behavior.
- [ ] Implement the Pydantic models and SQLite schema with migration versioning. Use transactions for writes, foreign keys for evidence references, and immutable event IDs independent of mutable names and dates.
- [ ] Run `python -m pytest tests/test_store.py -q` and confirm a pass.
- [ ] Record dependencies, a local setup command, and generated-data ignore patterns in the same change. Initialize a local Git repository when permitted by the workspace and commit this independently testable unit.

## Task 2 — Edition matching and shortlist continuity

**Files:** Create `tracker/match.py`, `tests/test_match.py`. Extend `tracker/store.py` only for merge and alias operations.

**Interfaces:** Produce `match_candidate(candidate: EventCandidate, existing: Sequence[EventCandidate]) -> MatchDecision` and `apply_match(store: EventStore, decision: MatchDecision) -> str`. `MatchDecision` distinguishes same edition, new edition, and possible duplicate. Task 3 uses it before saving fetched events.

- [ ] Write failing tests for a rescheduled event, renamed event, distinct annual edition, co-located event, uncertain fuzzy match, and confirmed merge of two shortlisted IDs. Assert identity and mark preservation.
- [ ] Run `python -m pytest tests/test_match.py -q` and confirm failure.
- [ ] Implement matching using publisher ID and official URL first, then organizer/series/edition/location/date evidence. Return a reviewable possible duplicate when evidence is insufficient. Keep aliases and reversible merge history.
- [ ] Run `python -m pytest tests/test_match.py tests/test_store.py -q` and confirm a pass.
- [ ] Commit the unit if Git is initialized.

## Task 3 — Source registry and real collection

**Files:** Create `config/sources.yaml`, `tracker/sources.py`, `tracker/collect.py`, `tests/test_collect.py`. Add small source-specific adapters under `tracker/adapters/` only when a verified source needs them.

**Interfaces:** Produce `load_sources(path: Path) -> list[SourceConfig]` and `collect_source(source: SourceConfig) -> SourceResult`. `SourceResult` contains observations, retrieval time, evidence references, and one of SUCCESS_WITH_EVENTS, SUCCESS_EMPTY, PARTIAL, FAILED, or BLOCKED. Task 6 runs these functions for enabled sources.

- [ ] Research and record actual official/public URLs before implementing adapters. Start with multiple NCR venue or organizer sources and at least one venue or organizer source each for Mumbai, Kolkata, and Bengaluru. Add a directory or search-discovered candidate source only when its public content is usable. Save date and observed extraction method for each verified entry.
- [ ] Write failing offline tests using saved representative HTML, JavaScript-rendered output, and PDF fixtures. Assert pagination, source URL and PDF page references, date parsing, and the previously-working-source-now-empty case.
- [ ] Run `python -m pytest tests/test_collect.py -q` and confirm failure.
- [ ] Implement direct feed/HTML/PDF extraction first, Scrapy orchestration for sites needing crawling, and Playwright only for sources where browser rendering or interaction is observed to be necessary. Add timeouts, bounded per-domain requests, retries for transient failures, and a manual URL/document intake route.
- [ ] Run `python -m pytest tests/test_collect.py -q` and confirm a pass. Execute a small live collection of verified public sources and inspect raw observations, source outcomes, and errors. Record any blocked or unreliable source honestly.
- [ ] Commit the unit if Git is initialized.

## Task 4 — Evidence-based assessment and optional AI batches

**Files:** Create `tracker/assess.py`, `tracker/batches.py`, `tests/test_assess.py`, `tests/test_batches.py`, and `config/classification_rules.md`.

**Interfaces:** Produce `assess_event(event: EventCandidate, evidence: Sequence[SourceObservation]) -> EventAssessment`, `export_batch(store: EventStore, output_path: Path) -> BatchManifest`, and `import_batch(store: EventStore, input_path: Path) -> ImportReport`. Task 5 reads stored assessments. Task 6 exposes batch commands.

- [ ] Write failing tests for eligible business products at a mixed leather/synthetic event, all confirmed restrictions, sparse evidence yielding UNKNOWN, a consumer-facing event with relevant brands, and equal industry baseline plus e-commerce tie-breaker.
- [ ] Write failing tests for stale AI results, malformed fields, invented evidence IDs, duplicate import, partial valid results, and AI output attempting to change a shortlist mark.
- [ ] Run `python -m pytest tests/test_assess.py tests/test_batches.py -q` and confirm failure.
- [ ] Implement conservative deterministic tags and participation reasons tied to evidence. Export bounded source-backed batches with schema and prompt version. Validate and import selected results transactionally without replacing newer evidence or shortlist state.
- [ ] Run `python -m pytest tests/test_assess.py tests/test_batches.py -q` and confirm a pass.
- [ ] Run one small manual batch through an existing Claude or ChatGPT subscription if the operator is available. Record its time and validation results. Keep deterministic assessment usable while the batch is pending.
- [ ] Commit the unit if Git is initialized.

## Task 5 — Populated workbook and shortlist round trip

**Files:** Create `tracker/workbook.py`, `tests/test_workbook.py`. Extend the store only for workbook shortlist import results.

**Interfaces:** Produce `export_workbook(store: EventStore, output_path: Path) -> WorkbookReport` and `import_shortlist(store: EventStore, workbook_path: Path) -> ShortlistImportReport`. Task 6 calls import before refreshing event data and export afterward.

- [ ] Write failing tests for an event table with filters, typed dates, source links, evidence year, explicit unavailable/projected metrics, shortlist mark, source-health sheet, and data dictionary. Include an edited shortlist mark that survives a second export, a rescheduled event, and an unfamiliar workbook ID.
- [ ] Run `python -m pytest tests/test_workbook.py -q` and confirm failure.
- [ ] Implement workbook export with openpyxl and shortlist import by immutable ID. Treat the active workbook as one operator copy. Back it up before refresh and replace it atomically after a validated export. Report unreadable, stale, or conflicting copies without losing marks.
- [ ] Run `python -m pytest tests/test_workbook.py -q` and confirm a pass. Open the populated workbook in a spreadsheet viewer available on the operating computer and inspect dates, widths, filters, links, and shortlist editing.
- [ ] Commit the unit if Git is initialized.

## Task 6 — Manual weekly workflow and pilot acceptance

**Files:** Create `tracker/cli.py`, `tests/test_cli.py`, `README.md`. Update `config/sources.yaml` as the pilot validates sources.

**Interfaces:** Expose `python -m tracker.cli refresh`, `python -m tracker.cli export-batch`, `python -m tracker.cli import-batch PATH`, and `python -m tracker.cli status`. A refresh first imports shortlist marks from the active workbook, collects sources, matches and assesses events, then safely exports the workbook.

- [ ] Write a failing end-to-end test for two refreshes, with a changed event date and an edited shortlist mark between them. Assert source failure retains prior valid data, a concurrent refresh cannot create two writers, and rerunning batch import is harmless.
- [ ] Run `python -m pytest tests/test_cli.py -q` and confirm failure.
- [ ] Implement CLI orchestration with clear per-source progress, collection and AI assessment freshness, recoverable errors, and a documented local setup/restore path. Keep the optional weekly schedule as a later operational step using the same refresh command.
- [ ] Run `python -m pytest -q` and confirm a pass. Run a manual live refresh and verify that actual event rows populate NCR, Mumbai, Kolkata, and Bengaluru or that each uncovered city/source has a visible documented gap. Compare a hand-checked set of known events and sample metric citations against the workbook.
- [ ] Ask Marketing and BD to inspect the populated tracker for omissions, duplicates, decision usefulness, and missing columns. Capture findings in `docs/tracker-pilot-findings.md` before planning the Python dashboard.
- [ ] Commit the unit if Git is initialized.

## Completion handoff

Deliver the populated workbook, source registry, pilot findings, setup instructions, and a concise gap report. The dashboard plan should use the fields and views that the pilot establishes. The optional weekly scheduler belongs to the next operating milestone and invokes the tested refresh command.
