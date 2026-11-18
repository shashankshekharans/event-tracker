# Event Tracker development plan

Prepared for an India-focused warehousing and transportation business. Revised 18 November 2026.

Status — Business requirements consolidated from the discussion. Technical proposals below are ready for confirmation and implementation planning.

## 1. Purpose and agreed requirements

Help Marketing and Business Development discover events early, shortlist useful opportunities, and assess whether the business should visit, exhibit, speak, or sponsor. Management will discuss the shortlist after the internal teams have assessed it.

| Area | Confirmed direction |
| --- | --- |
| Geography | Start with Delhi NCR, Mumbai, Kolkata, and Bengaluru. Give NCR special emphasis. Expand to other metros and Tier-2 cities. |
| Industries | Give all listed industries equal baseline importance, with a modest preference for B2B and B2C e-commerce businesses. |
| Event evaluation | Include event type, edition, exhibitors, footfall, and other available metrics that help participation decisions. |
| User interaction | Provide a persistent shortlist mark and a shortlisted-only filter. Team and management discussions happen around this shortlist. |
| Refresh | Weekly cadence, with both manual and scheduled options. Start operating with manual refresh. |
| Cost | Zero additional software, hosting, search, scraping, or AI API expenditure. Use existing hardware, connectivity, and Claude/ChatGPT subscriptions. |
| AI access | Use export/import batches with existing subscriptions. API access is unavailable. |
| First delivery | A populated local Excel-compatible event tracker that lets the team inspect real listings and mark shortlisted events. |
| Later delivery | Build a custom Python browser dashboard after evaluating the tracker, then move the dashboard to React. Consider Cloudflare subsequently. |
| Browser collection | Playwright is permitted where useful. |
| Dashboard framework | A custom dashboard is required. Streamlit is excluded. |

The planning horizon carried forward from the original brief is November 2026 through December 2027. Upcoming views use the current date. Historical editions can supply evidence about an event's track record.

Success means an evidence-backed, usable shortlist, visible collection gaps, and shortlist marks that survive refreshes and changes to an event. The populated tracker must show whether the discovered events and available evidence are useful before dashboard work begins.

### Current implementation checkpoint — 18 November 2026

The Excel tracker is the Stage 0 review tool. Start Here links to the Events schedule, Dates Pending, Speaker Opportunities, Awards and CEO Opportunities, and the evidence reference sheets. The latest edition audit reconciled 224 event records into 73 scheduled entries and 151 pending entries. The 200+ scheduled-event target remains open. Use sourced historical timing or an organizer's announcement to set planning windows for pending entries.

The workbook has eight speaker routes and nine awards, competition or leadership leads. Separate Yes/No shortlists support internal review. Event marks follow the event between the schedule and pending worksheets. During the workbook pilot, the team can assess the value of these fields for the later browser dashboard.

The local Python collector uses reviewed source records, bounded sequential crawling, a short-lived local cache and guarded redirects. The most recent crawl checked 20 registered sources, fetched 37 pages, found 209 unique candidate links and staged 239 accumulated candidate records.

10times, WHR.ai, AllEvents, WeMilap, India Expo Centre & Mart, sources returning access restrictions, and sources awaiting permission review remain disabled. Continue adding only source-backed event editions and report the source coverage limit if permitted sources do not reach 200.

## 2. Approaches and staged architecture

The user selected a tracker-first rollout, followed by a custom Python dashboard and then React. The specific frameworks in the following design are engineering proposals.

| Approach considered | Trade-off | Decision |
| --- | --- | --- |
| Python with Streamlit | Quick dashboard implementation, with a Python server required for online access. | Rejected by the user. |
| React dashboard from the start | Flexible interface and an established Cloudflare frontend deployment path, with more initial frontend work. | Reserved for the second stage. |
| Python with a custom HTML dashboard | Python handles collection, processing, persistence, and server-rendered pages. HTML/CSS provides the browser interface. | Proposed first-stage implementation of the user's selected Python-first approach. |

The tracker-first approach adds a discovery and validation stage before building either dashboard. A local .xlsx workbook is the proposed primary tracker because the first rollout runs locally. Exporting its event table as CSV keeps Google Sheets available if the team later prefers it. Use free Python libraries for creating the workbook, with no purchase required to generate it. Confirm a suitable spreadsheet viewer on the operating computer during setup.

### Stage 0 — Populated event tracker and source pilot

Build a Python collection and normalization path for representative sources in NCR, Mumbai, Kolkata, and Bengaluru. Populate the tracker with real upcoming events, their source links, product-suitability indicators, and the decision metrics available from each source. Begin with NCR to test the deeper coverage requirement. The team inspects actual entries and shortlist marks, then adjusts fields, source priorities, and ranking before the browser dashboard is designed.

Use one event-edition ID per row. Separate the event table from a source-health sheet and a short data dictionary. The event table should show identity, date certainty, location, type, edition, organizer, eligible industries and product lines, exhibitor names/count, footfall with reporting year, booking deadline where published, participation options, evidence links, last checked date, suitability reason, missing information, and a shortlist mark. Keep the table filterable. Any new columns should answer a decision the team actually makes.

The tracker is a working deliverable, with weekly manual refresh and persistent shortlist marks. Before each refresh, Python reads shortlist marks from the single local workbook and validates its event IDs. It then updates event facts and writes a refreshed workbook with those marks intact. A changed date or venue updates the existing row. A new annual edition receives its own row. A separate source-health sheet shows failed or incomplete collections so an empty event table cannot appear to mean that no events exist. Keep a dated backup before replacing the workbook, and report unfamiliar IDs or conflicting copies for operator resolution.

Evaluate the tracker using a hand-checked sample of known events. Record missed events, duplicates, incorrect suitability tags, missing decision metrics, and the time needed for weekly maintenance. Fix these gaps before committing to the dashboard layout.

### Stage 1 — Local Python dashboard

Proposed stack is FastAPI, Jinja2 templates, custom HTML/CSS, SQLite, Scrapy, Playwright where required, pdfplumber, and Pydantic. Small amounts of browser JavaScript may improve interactions when necessary. Python owns the application logic. FastAPI supports templates and static assets. [FastAPI documentation](https://fastapi.tiangolo.com/advanced/templates/)

The application runs on the user's Windows computer and opens in a browser. Proposed default is access from that computer through localhost, with one shared shortlist in its database. Import the validated tracker data and marks into SQLite. Continue to provide spreadsheet exports for meetings.

Keep event collection, import validation, matching, ranking, and shortlist operations outside template code. Both the initial pages and the later React UI should call the same application operations.

### Stage 2 — React dashboard

Replace the presentation layer with React while retaining stable event IDs, event evidence, collection logic, and shortlist state. Expose the required application operations through a local HTTP API. This stage can continue running locally.

### Stage 3 — Optional online deployment

Cloudflare is a possible later hosting choice. Its supported React deployment path covers the frontend. Shared online storage, authentication, and a route for publishing local refresh results require a separate deployment design that fits the zero-additional-cost constraint. [Cloudflare React documentation](https://developers.cloudflare.com/pages/framework-guides/deploy-a-react-site/)

## 3. Geographic and industry scope

### Geographic rollout

1. Validate NCR sources first, then cover Mumbai, Kolkata, and Bengaluru for the first-stage release.
2. Extend coverage to Hyderabad, Chennai, Pune, Ahmedabad, and additional metros.
3. Add Tier-2 cities through an explicit city registry and verified source coverage.

NCR receives deeper source discovery and higher geographic priority in ordering. Store actual city and metro region separately so Greater Noida, Noida, Gurugram, Faridabad, Ghaziabad, and New Delhi can be viewed together without losing venue location. A business-defined city registry controls rollout and labels.

Preserve records discovered outside the current rollout area and label their coverage status. Distinguish a city with checked sources from a city where coverage remains incomplete.

### Customer industries

- D2C, B2B/B2C e-commerce, omnichannel retail, and retail technology.
- Apparel, fashion, textiles, sportswear, and eligible footwear.
- Book publishing, stationery, printing, and relevant education businesses.
- Consumer electronics, accessories, and appliances.
- Automotive, EV, engineering components, and aftermarket businesses.
- Pharmaceuticals, nutraceuticals, healthcare devices, wellness, and Ayurveda products within the warehouse storage restrictions.
- Sports, fitness, and health goods.
- Home, kitchen, furniture, decor, lifestyle, and gifting.
- Industrial and general manufacturing, packaging, polymers, chemicals, hardware, and tools, subject to product suitability.
- Eligible FMCG, cosmetics, personal care, home care, and shelf-stable goods subject to the confirmed exclusions.

An industry label does not establish product eligibility. B2B/B2C e-commerce is a business-model tag that can apply across these industries.

### Event relationships and formats

Use multiple relationship tags when appropriate, including CLIENT_VERTICAL and PEER_LOGISTICS. Retain UNASSESSED when evidence is insufficient. Mark an event IRRELEVANT only when available evidence supports that decision. A consumer-facing event may still contain useful exhibiting businesses.

Support EXHIBITION, CONFERENCE_SUMMIT, ROUNDTABLE, AWARDS_NETWORKING, MIXED, OTHER, and UNKNOWN. Record exhibitor counts separately. A published count of at least 100 can support a large-expo label, while smaller and unknown-size events remain eligible.

## 4. Product suitability and ethical alignment

Confirmed warehouse exclusions are leather, perishable food, products requiring temperature-controlled storage, alcohol, and meat-based products, including meat-based pet food.

The team can pursue the eligible product lines of a business that also sells restricted products. An expo with separate synthetic-footwear and leather sections can be useful for the synthetic-footwear opportunity.

Proposed event indicators are as follows.

| Indicator | Meaning |
| --- | --- |
| GREEN | Evidence supports relevant product opportunities within the confirmed restrictions, with no identified concern in the assessed scope. |
| AMBER | Mixed eligible and restricted products, or a specific suitability question needing attention. Show the eligible opportunity and the concern. |
| RED | Evidence establishes a restricted focus and offers no identified eligible customer opportunity within the assessed scope. |
| UNKNOWN | Available information is insufficient to assess product suitability. |

Keep AMBER and UNKNOWN visible by default. RED remains accessible through a filter. Any shortlisted event stays accessible in the shortlist even if its suitability or schedule later changes.

GREEN must carry the scope and evidence behind the assessment. It is an event-discovery indicator and does not certify every exhibitor or product.

Keyword matches create evidence candidates. Context must distinguish terms such as synthetic leather, meat-free products, water-related uses of "aqua," and ordinary words containing short keywords. The presence of a restricted word alone cannot determine the entire event's suitability.

AI proposes the indicator, eligible product opportunities, and reasons from supplied evidence. Missing evidence stays UNKNOWN. New evidence may revise the indicator while preserving the shortlist mark.

Dairy, shelf-stable food processing, and non-meat pet products require assessment against the confirmed restrictions. The original draft's broader exclusions for these categories remain unconfirmed and should surface as policy questions where relevant.

## 5. Information needed for participation decisions

Each event profile should expose the following fields when published.

| Group | Information |
| --- | --- |
| Identity | Event name, edition, organizer, official website, source links, description, and event format. |
| Schedule | Start/end dates, date certainty, venue, city, region, and scheduled/postponed/cancelled/completed status. |
| Exhibitors | Named companies, product categories, exhibitor count, source edition, and eligible opportunities for the business. |
| Audience | Footfall, unique visitors where specified, buyer or decision-maker profiles, attendee industries, geography, and B2B/B2C e-commerce presence. |
| Scale and track record | Exhibition area, conference attendance, previous editions, and published post-show reports. |
| Participation | Stall pricing and units, minimum space, taxes where stated, delegate charges, booking deadlines, exhibitor enquiry links, sponsorship, speaking, and award opportunities. |
| Business assessment | Industry fit, product suitability, geography, evidence strength, suggested participation options, reasons, and missing information. |
| Freshness | Last successful observation, current source failures, changed facts, and pending AI processing. |

Every metric must include value, unit, edition or reporting period, publisher, source URL or document reference, retrieval time, and a supporting excerpt or PDF page where possible. Label organizer projections, organizer-reported historical results, and independently reported results accurately.

Treat visits and unique visitors as different measures. Keep last year's footfall attached to last year's edition. Missing figures remain unavailable. Conflicting values remain traceable to their sources.

A booking-deadline alert requires a published booking deadline. Time until the event may support a planning reminder. Record both concepts separately.

## 6. Prioritization and participation suggestions

Use transparent, configurable rules for the first stage. Give all industries equal baseline importance. Propose NCR as the first geographic sorting preference, followed by evidence of eligible target customers, the modest e-commerce preference, and event date. Users can change ordering and filters.

Show reasons for the priority. Keep evidence completeness visible so a sparsely documented opportunity can still be investigated. The original unexplained 1–10 customer-density score is replaced by evidence-backed dimensions until a scoring rubric can be calibrated against real events.

Suggest one or more of VISIT_FOR_BD, CONSIDER_STALL, EXPLORE_SPEAKING_SPONSORSHIP, or NEEDS_INFORMATION. A stall suggestion should cite relevant exhibitor/audience evidence and available participation details. Where cost or audience evidence is missing, show the gap alongside the suggestion.

The tool supports Marketing/BD's initial assessment and management's discussion through the event profile and shortlist. A shortlist mark represents interest in considering the event.

## 7. Collection and discovery

Preserve four source layers — venues, associations, organizers, and directories/search discovery. The candidate catalog at the end of this document carries forward the original source names. Each source needs actual URL verification and an access/extraction assessment.

### Source registry

For each source, record ID, URL, publisher, source layer, cities/industries covered, fetch strategy, expected content type, enabled state, last attempt, last successful fetch, extraction version, content hash, and current error.

Distinguish SUCCESS_WITH_EVENTS, SUCCESS_EMPTY, PARTIAL, FAILED, and BLOCKED. Detect suspicious empty results when a previously working page changes structure. A failed source retains its last good data with a freshness warning.

### Fetch strategy

1. Use public feeds, downloadable files, structured event data, and accessible data endpoints where available.
2. Use Scrapy for HTML collection, pagination, and following relevant event links.
3. Use Playwright for sources requiring JavaScript rendering or page interaction.
4. Extract text and tables from PDFs with pdfplumber. Route scanned pages through a free local OCR tool when needed and label extraction quality.
5. Allow an operator to add a URL or import a saved public document for sources that remain inaccessible.

Scrapy documents direct-source extraction and browser handling for dynamic content. Playwright provides Python browser automation, and pdfplumber supports text and table extraction from PDFs. [Scrapy documentation](https://docs.scrapy.org/en/latest/topics/dynamic-content.html) · [Playwright Python documentation](https://playwright.dev/python/docs/intro) · [pdfplumber documentation](https://github.com/jsvine/pdfplumber)

Use bounded concurrency, per-domain request delays, retries for transient failures, timeouts, caching, and resumable source jobs. Preserve source snapshots used as evidence. Log source failures visibly.

### New-source discovery

Known-source collection follows relevant event and organizer links. Discovery is not restricted to the catalog above: search India-wide across official organizers, venues, trade bodies, government and embassy trade calendars, and credible directories. Prioritize NCR, then Mumbai, Kolkata, and Bengaluru, then other metros and Tier 2 cities. Generate focused search query links by city, vertical, event type, and year for an operator's weekly discovery sweep. The operator can add useful results to the registry.

Treat annual calendars and embassy listings as discovery evidence, not an exhaustive census. Prefer an event's organizer or venue page for its dates; retain government/embassy corroboration where available. Label tentative or conflicting dates, and keep announced 2027 editions with dates pending separate from dated event rows. Track coverage by month, city, and source layer through December 2027 so sparse months trigger more discovery. The initial 65-row workbook is a working seed, not completion of the requested event database.

The free baseline relies on direct crawling and operator-assisted search. Keep web research credit-light by batching focused queries, caching page/source revisions, and searching again only for gaps or changed pages. Automated search discovery can be added only after verifying a usable zero-cost route and its limits. Discovery coverage must show this manual dependency.

## 8. Subscription-based AI processing

1. Collect and normalize source facts locally.
2. Create bounded batches of new or changed records containing evidence, a versioned prompt, schema, batch ID, and immutable candidate IDs.
3. Let the operator download the batches and process them in their existing Claude or ChatGPT account.
4. Import the returned structured results through the local application.
5. Validate each result before publishing it to the event database.
6. Show pending, rejected, and accepted results so the operator can retry only unfinished work.

The baseline AI handoff uses manual export/import within the existing subscriptions. Subscription limits can delay processing. Collection and the populated tracker remain usable while batches are pending. The later dashboard shows the same pending state. Chat subscriptions and API billing are separate systems. [OpenAI billing documentation](https://help.openai.com/en/articles/9039756-managing-billing-for-chatgpt-and-the-api-platform) · [Anthropic billing documentation](https://support.anthropic.com/en/articles/9876003-i-subscribe-to-a-paid-claude-ai-plan-why-do-i-have-to-pay-separately-for-api-usage-on-console)

AI extracts and assesses supplied evidence. Source text is treated as untrusted input. Preserve factual claims with their evidence references and flag unsupported claims. Import validation checks field types, allowed values, referenced candidates, evidence IDs, dates, nonnegative metrics, and required suitability reasons.

Associate results with the source revision that produced their batch. If the event evidence changes before import, flag stale results and regenerate the affected work. Repeated imports are idempotent. AI output cannot write shortlist state.

## 9. Data model and persistence

SQLite is the proposed authoritative local store for source evidence, event identities, and refresh runs from the pilot onward. The .xlsx workbook is the operator's first-stage view and the input for shortlist marks until the browser dashboard is built. Import the marks by immutable event-edition ID before each refresh, then export the refreshed workbook from SQLite. JSON and CSV support batch exchange and exports. Keep one active workbook to avoid conflicting edits.

| Entity | Core content |
| --- | --- |
| Event series | Stable identity of a recurring event and its organizer. |
| Event edition | Immutable ID, series link where known, edition/year, names and aliases, location, dates, status, and revision. |
| Source record | Publisher record or URL, observed content, retrieval time, content hash, and canonical event link. |
| Fact or metric | Field, value/unit, edition, forecast/history status, evidence reference, and source confidence. |
| Assessment | Relationship/vertical tags, product opportunities and exclusions, suitability, evidence references, suggested actions, and processing revision. |
| Shortlist | Event-edition ID, marked/unmarked state, and last change time. |
| Refresh run | Start/end, per-source outcomes, errors, counts, and recovery state. |
| AI batch | Batch and candidate IDs, evidence revisions, prompt/schema versions, import outcome, and pending items. |

Use actual date types and validated URLs. Allow uncertain dates, unknown venue/edition, and multiple industry/format tags. Enforce end date on or after start date when both are known. Store precise dates only when supported. An announced 2027 event with dates pending can appear in a dates-to-be-announced view.

Separate recurring editions so a 2026 shortlist does not automatically transfer to 2027. Preserve facts from historical editions as historical evidence.

### Identity and deduplication

Assign an immutable event-edition ID on first acceptance. Names, dates, and cities can change without changing that ID.

Match using publisher IDs, canonical event links, organizer, series, edition, city, venue, dates, and name aliases. Fuzzy names and date proximity identify candidates. They alone cannot establish a match.

Treat rescheduling, rebranding, relocation, recurring editions, and co-located events explicitly. Keep uncertain matches as possible duplicates for operator resolution. Confirmed merges retain source history and aliases, and preserve a positive shortlist mark if either record was marked. Maintain merge history so a mistaken merge can be corrected.

Prioritize explicit organizer corrections and edition-specific official announcements when resolving conflicts. Retain contradictory observations and flag unresolved schedule conflicts. A vanished page or failed crawl alone cannot mark an event cancelled.

### Safe writes and recovery

Use transactions for imports, merges, and shortlist updates. Ensure collection cannot overwrite shortlist state. Permit one refresh writer at a time, including overlap between a scheduled run and a manual request. Keep reads responsive while collection runs.

Create a recoverable database backup before schema migrations and bulk imports/merges. A failed batch or failed source leaves the previous valid records available. Keep a documented restore procedure.

## 10. First-stage dashboard behavior

Provide a custom browser interface served by Python, with clear labels, keyboard-accessible controls, readable tables, and layouts that fit laptop screens and narrow windows. Detailed visual styling is an implementation design task.

The primary view includes event name, date/date certainty, city, type, suitability, priority reasons, freshness, and a shortlist control. Open an event profile to inspect metrics, exhibitors, participation details, and evidence links.

Provide filters for city/region, dates, industry, business model, relationship, event format, suitability, and shortlisted-only. Default to upcoming client opportunities across the enabled first-stage geography, with NCR prominent. Keep peer logistics available through a toggle.

Show shortlist count, relevant upcoming events, new/changed events since the previous successful run, and collection health. The shortlisted view also exposes cancelled, past, or newly restricted marked events with their current status.

Provide manual refresh, run progress, AI batch export/import, source problems, and filtered CSV/Excel export. Persist shortlist marks in SQLite and restore them after restarts. User actions set an explicit marked state so retries cannot accidentally flip a mark twice.

## 11. Manual and scheduled refresh

Manual operation is the starting mode. A refresh collects source changes, updates validated facts, reconciles event identities, and prepares pending AI batches. The operator performs the AI export/import step.

Offer a weekly scheduled collection option using the same command and run pipeline. Proposed Windows implementation uses Task Scheduler. Display the configured schedule and last completion. If the computer is off, show the overdue refresh and run at the next configured opportunity.

Scheduling collection does not complete a pending manual AI batch. Show collection freshness and assessment freshness independently. Preserve old assessments with their revision and stale state when newer evidence is awaiting processing.

## 12. Delivery milestones and verification

### Milestone 1 — Populate and inspect the event tracker

Check representative NCR sources across all four layers, plus a representative venue/organizer source in each other first-stage metro. Include an HTML calendar, a JavaScript page, a PDF, a recurring edition, and a conflicting or incomplete listing.

Produce the source registry, a hand-checked benchmark, and a populated .xlsx workbook with cited event facts, a shortlist column, source-health sheet, and data dictionary. Run a manual weekly refresh cycle and inspect the resulting listings with Marketing and BD. Record missed events, duplicates, missing metrics, source failures, and AI batch workload. Adjust source and data priorities from this evidence before dashboard design.

### Milestone 2 — Build the custom local Python dashboard

Build the custom dashboard around the fields and filters that proved useful in the tracker. Reuse the collection, evidence storage, subscription batch exchange, validation, stable event identity, shortlist persistence, and exports established in Milestone 1. Exercise the manual refresh path from the browser through to imported classifications.

### Milestone 3 — Weekly operation and broader coverage

Add the optional scheduled run, recovery behavior, and source-health reporting. Complete first-stage city coverage against the named source registry, then extend it to other metros and Tier-2 cities.

### Milestone 4 — React migration

Build the React dashboard against the existing application operations. Verify matching filters, evidence, exports, and preserved shortlist state before adopting it.

### Milestone 5 — Optional Cloudflare deployment

Reassess hosting/storage limits and access needs at deployment time. Select an online architecture that meets the cost requirement and handles shared shortlist persistence.

### Acceptance criteria for the tracker-first release

- Every enabled source reports a meaningful outcome for the run.
- Every event in the hand-checked source benchmark is recovered or has an explicit documented collection gap.
- All four initial metro areas have verified active sources, with deeper NCR coverage documented.
- Sampled event dates, editions, exhibitors, and metrics match their cited evidence.
- Missing and projected metrics are labelled accurately.
- Mixed synthetic/leather opportunities remain visible with an explanation.
- B2B/B2C e-commerce companies can qualify across industries.
- Rescheduling, renaming, merging, cancellation, and refresh preserve shortlist marks.
- Separate annual editions retain separate identities.
- Invalid or stale AI imports cannot silently overwrite newer valid facts.
- Repeat imports and overlapping refresh requests leave consistent records.
- The populated workbook opens in an available spreadsheet viewer and supports filtering, source inspection, and shortlist marking.
- Manual refresh, batch import, workbook filtering, shortlisting, restart, and export work through normal operator entry points.
- Shortlist marks entered in the active workbook survive a weekly refresh and can be carried into the later dashboard.
- A restored backup recovers both events and shortlist state.
- The baseline workflow operates using free tools and the existing subscriptions.

Test the regression cases that protect event identity, evidence, batch imports, and shortlist persistence. Measure completeness against checked sources and known events. Report unverified sources and discovery gaps explicitly.

## 13. Repository and implementation boundaries

Proposed structure follows the application's responsibilities.

```text
config/          Sources, city mappings, classification rules, search queries
scraper/         Source adapters, document extraction, collection jobs
processor/       Normalization, evidence validation, AI batch export/import
storage/         SQLite schema, migrations, event matching, shortlist operations
tracker/         Workbook generation, shortlist import, data dictionary
dashboard/       Python routes, HTML templates, CSS, browser interactions
data/            Local database, source snapshots, batches, backups, exports
tests/           Focused regression and workflow verification
requirements.txt
```

Carry forward GitHub synchronization for source code, configuration, and reproducible schemas. Keep local databases, raw downloads, generated batches, and machine-specific configuration outside routine Git tracking. The workspace currently contains the plan and has no initialized Git repository.

Framework choices, default ranking order, local single-database operation, source retention, OCR selection, and exact matching thresholds are engineering proposals or implementation details. Calibrate thresholds and retention from the pilot. Keep policy uncertainties visible instead of silently expanding the confirmed exclusions.

## 14. Changes from the original plan

The revised plan replaces the zero-missed-events guarantee with measurable coverage and source health. It adds evidence for decision metrics, stable edition identities, safe imports, and recovery behavior.

It reflects the user's product-level eligibility rule, equal industry baseline with an e-commerce preference, NCR emphasis, weekly/manual-first refresh, shortlist-only interaction, zero additional cost, tracker-first evaluation, staged Python-to-React delivery, optional Playwright use, and a custom dashboard.

The proposed FastAPI/Jinja2 implementation and local database design need confirmation as part of this design. Detailed implementation planning follows design approval.

## Appendix — Candidate source catalog

These are research candidates carried forward from the original plan. Their current URLs, calendars, accessibility, completeness, and extraction behavior require verification during the source pilot.

### Layer 1: Pan-India Exhibition Centres & Venues (Direct Master Calendars)
Check each venue for public event calendars, announcements, and downloadable schedules. Publication lead times must be established from observed sources.

| Region / City | Target Exhibition Centres to Scrape |
| :--- | :--- |
| **Delhi-NCR** | • **Yashobhumi (IICC)**, Dwarka<br>• **Bharat Mandapam (ITPO / Pragati Maidan)**, New Delhi<br>• **India Expo Centre & Mart (IEML)**, Greater Noida<br>• **A Dot by GNH / Huda Ground**, Gurugram |
| **Mumbai & Pune** | • **Bombay Exhibition Centre (NESCO)**, Goregaon<br>• **Jio World Convention Centre (JWCC)**, BKC<br>• **CIDCO Exhibition & Convention Centre**, Vashi, Navi Mumbai<br>• **World Trade Center (WTC)**, Cuffe Parade<br>• **Pune International Exhibition and Convention Centre (PIECC)**, Moshi<br>• **Auto Cluster Exhibition Center**, Chinchwad, Pune |
| **Bengaluru** | • **Bangalore International Exhibition Centre (BIEC)**, Tumkur Road<br>• **KTPO (Karnataka Trade Promotion Organisation)**, Whitefield<br>• **Tripura Vasini / Palace Grounds**, Bengaluru<br>• **NIMHANS Convention Centre** |
| **Hyderabad** | • **HITEX Exhibition Centre**, Madhapur<br>• **HICC (Hyderabad International Convention Centre)**, Novotel |
| **Chennai & South Tier-2** | • **Chennai Trade Centre (CTC)**, Nandambakkam<br>• **CODISSIA Trade Fair Complex**, Coimbatore<br>• **Adlux International Convention & Exhibition Centre**, Kochi |
| **Ahmedabad & West Tier-2** | • **Helipad Exhibition Centre (Exhibition Center Gandhinagar)**<br>• **Gujarat University Convention and Exhibition Centre (GUCEC)**, Ahmedabad<br>• **vigyan Bhavan / SIECC (Surat International Exhibition and Convention Centre)**, Surat |
| **Kolkata & East** | • **Biswa Bangla Mela Prangan (Milan Mela)**, Kolkata<br>• **Biswa Bangla Convention Centre**, New Town, Kolkata |
| **North & Central Tier-2** | • **JECC (Jaipur Exhibition & Convention Centre)**, Sitapura, Jaipur<br>• **Labh Ganga Exhibition Center**, Indore<br>• **Indira Gandhi Pratishthan**, Lucknow |

### Layer 2: Trade Bodies, Associations & Chamber Portals
* **National Chambers:** CII (`cam.cii.in`), FICCI (`ficci.in/events`), ASSOCHAM, PHDCCI, IMC Chamber of Commerce.
* **Retail, E-Commerce & D2C Bodies:** Retailers Association of India (**RAI**), Indian Retailer / Franchise India, **Images Group** (India Fashion Forum, India D2C Summit, Phygital Retail Convention), **ETRetail / Economic Times B2B** (`retail.economictimes.indiatimes.com/events`), **Inc42** (D2C Summit), **e4m (Exchange4Media)**, **IAMAI**.
* **Vertical-Specific Associations:**
  * *Publishing:* National Book Trust (NBT - World Book Fair), FIP (Federation of Indian Publishers).
  * *Auto & EV:* ACMA (Automotive Component Manufacturers Association), SIAM.
  * *Apparel & Textiles:* CMAI (Clothing Manufacturers Association of India), Bharat Tex.
  * *Pharma & Health:* IPA, IDMA, CPHI India.

### Layer 3: Major B2B Exhibition Organizers (India Portfolios)
Scrape the "Upcoming Events - India" pages directly from:
* **Informa Markets India**
* **RX India (Reed Exhibitions)**
* **Messe Muenchen India**
* **Messe Frankfurt India**
* **Koelnmesse India**
* **NürnbergMesse India**
* **Trescon / Alden Global / Verve Management / Exito Media / Kamikaze B2B Media**
* **ABEC (Asian Business Exhibitions & Conferences - Acetech, etc.)**
* **Mex Exhibitions / Fairfest Media / Services International**


### Layer 4 — Directories and search discovery

Candidate directories include 10times, WHR.ai, AllEvents, Eventbrite, Townscript, and TradeFairDates. Verify each candidate's current availability and usefulness.

Prepare focused search links combining one city/region, an event type, a customer vertical, and a relevant year. Include NCR aliases and the other first-stage metros. The operator uses these links during the weekly discovery sweep and imports promising URLs.

Store search findings as candidates until the event details can be checked against organizer, association, venue, or other supporting evidence.
