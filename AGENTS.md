# Event Tracker agent handoff

Start with [the product plan](PRODUCT_PLAN.md) for business rules and [the README](README.md) for the operating workflow. The dated plans in docs/superpowers describe earlier implementation stages. Use the 18 November 2026 audit as the current baseline.

## Where development stopped

The Python workbook pilot is live. The 18 November 2026 refresh reconciled 224 records into 87 scheduled editions and 137 pending records. Eight speaker routes and nine leadership opportunities have independent shortlist marks. There are 118 records marked Evidence pending, including 25 in Delhi NCR; continue research with the remaining NCR queue. The registry has 26 sources: 14 enabled, seven disallowed by policy, one access-blocked and four awaiting review. The 18 November source audit and domain queue are in `docs/source_coverage_audit_2026-11-18.md` and its companion CSV. The workbook Source Health view distinguishes evidence links from crawl outcomes. Gather Marketing and BD feedback before developing the custom Python dashboard, then React. Streamlit is excluded. Keep the solution local and free of paid APIs.

## Code and data

- tracker/cli.py is the entry point for refresh, scan and status. Run it from the repository root.
- tracker/collect.py reads reviewed source policies. tracker/candidates.py stages discovery leads. Follow registry access decisions and rate limits.
- tracker/event_status.py determines schedule eligibility. Historical planning estimates need a prior date and source. A current edition-specific organizer call is required for an OPEN speaker opportunity.
- tracker/store.py maintains immutable IDs and SQLite shortlist marks. tracker/workbook.py and tracker/workbook_views.py generate the Excel views and import marks. Preserve event keys when updating dates or venues.
- data/verified_events.json includes pending as well as scheduled records. Check audit_status before using a row. Target ambient, non-perishable product lines. Mixed businesses may have eligible lines.
- Keep the local working database, workbook, backups, response cache and extracted calendar text out of Git. docs/Event_Tracker.xlsx is a published preview generated from the seed data with empty shortlists and current Source Health labels.
- For older installations, close Excel and copy data/AAJ_Event_Tracker.xlsx to data/Event_Tracker.xlsx once alongside its existing database before refreshing. The original workspace has already been migrated.

## Working agreement

Use Superpowers for development workflow, Impeccable for UI/UX and Matt Pocock skills for focused engineering review when available. Load only the skills needed. Run the existing suite with python -m unittest discover -s tests -v. Check refresh on disposable data for shortlist or schema changes. For a release, reconcile the worksheet counts, verify Start Here navigation, and update the dated README snapshot and downloadable preview together.
