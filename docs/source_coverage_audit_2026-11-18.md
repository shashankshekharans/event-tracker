# Source coverage audit — 18 November 2026

## What the Source Health labels mean

The workbook combines two different inventories. `BLOCKED` means a registered source scan was denied by source policy or access controls. `EVIDENCE LINK (NOT SCANNED)` means an event record links to evidence that is not itself a logged crawl URL; it does not mean a request failed. The refreshed workbook has 205 evidence links not scanned, nine blocked source rows, 13 sources with event candidates and one successful empty scan. The Source Health tab shows the publisher domain and registry decision next to each scan or evidence link.

The 224 event records use 149 distinct primary source domains and 158 domains when corroborating and prior-edition links are included. Of those 158 domains, 139 are absent from the 26-source registry. By primary event record, 39 use enabled source domains, 17 use disabled domains (10 disallowed, seven review required, one access blocked), and 167 use unregistered domains. Registry membership does not mean that an individual event page was fetched.

The first 18 November scan fetched 38 pages across 23 registered sources and produced 212 unique candidate links. The targeted follow-up checked Gifts World and Medicall at one page each; the duplicate Gifts World source row was consolidated. The merged log now has 23 source records, 39 fetched pages, 226 raw candidate links and 217 unique candidate links. The current registry has 26 sources: 14 enabled, seven disallowed by policy, one access blocked and four still under policy review. The candidate list is for discovery, not a verified event count.

The targeted Gifts World scan now finds four dated city-edition links (Mumbai, Kolkata, Delhi and Bengaluru) from its dated homepage cards. Medicall's homepage scan found one stale 2020 structured event; current edition dates are still checked from the official schedule, and the stale candidate must not be counted as new. ITPO's event listing returned an Angular app shell with no event links in static HTML. A one-time inspection of the public JavaScript bundle did not reveal a clear public data endpoint; inspect the browser's normal network requests before selecting a fallback. No access-control bypass was attempted.

The domain inventory is in [source_coverage_domains_2026-11-18.csv](source_coverage_domains_2026-11-18.csv). Counts come from the event seed, source registry, merged crawl log and generated workbook. This is a local audit plus focused live checks, not a reachability test of every domain.

## Highest-value source review queue

The first queue favors Delhi NCR, warehousing and transportation, e-commerce, and domains that support multiple event records. This ordering guides review effort; it does not override the equal baseline importance of other industries.

| Domain | Primary records | NCR records | Evidence pending | First action |
| --- | ---: | ---: | ---: | --- |
| `indiaexpomart.com` | 7 | 7 | 0 | DISALLOW; request permission or use manual evidence review. |
| `itpo.gov.in` | 7 | 5 | 5 | Inspect the Angular page's public data requests; keep manual organizer pages meanwhile. |
| `convergenceindia.org` | 3 | 3 | 0 | Keep under review while robots signals and AI-input terms are clarified. |
| `acetechexpo.com` | 5 | 2 | 2 | Confirm NCR and other city editions; keep estimates distinct from announced dates. |
| `cii.in` | 5 | 1 | 2 | Find official event, award and case-competition calendars. |
| `cphi.com` | 2 | 2 | 1 | Confirm 2027 edition details and automated access rules. |
| `medicall.in` | 3 | 1 | 2 | Enabled for factual crawl; add a current-date filter for stale structured events. |
| `hghindia.com` | 2 | 1 | 2 | Confirm the Greater Noida and Mumbai 2027 editions. |
| `smarthomeexpo.in` | 2 | 1 | 2 | Confirm whether a Delhi NCR edition exists for 2027. |
| `indiawarehousingshow.com` | 2 | 2 | 0 | DISALLOW automated commercial collection under the reviewed site terms. |
| `giftsworldexpo.com` | 4 | 1 | 0 | Enabled; dated card links are now discovered in the one-page scan. |
| `renewableenergyindiaexpo.com` | 2 | 2 | 1 | Reconcile the organizer's October and November 2027 date conflict. |

`indiaexpomart.com` and `indiawarehousingshow.com` remain excluded from automated commercial crawling under their reviewed terms. Their public facts can still be checked manually. `indiawood.com` robots are now accessible, but its terms limit access to personal use and restrict copying/redistribution, so it is marked DISALLOW for AAJ automation. Gifts World Expo and Medicall are now enabled for low-rate collection of public event facts after checking robots and site terms. Convergence India remains under review because its robots content signals restrict AI input; do not feed its pages into AI processing until that scope is clarified. 10times and other event directories with commercial-use restrictions remain excluded from automated collection.


## Record updates from live official-source review

- Verified eight previously pending dates/editions: India Warehousing Show 2026 (25–27 June, historical), ACMA Automechanika New Delhi 2026 (5–7 February, historical), IPHEX Delhi 2027 (19–21 August), D-arc BUILD New Delhi 2027 (23–26 September), IFAT Delhi 2027 (21–23 April at Bharat Mandapam), Delhi Jewellery & Gem Fair 2027 (18–20 September), Toy Biz 2027 (3–6 July), and International Hardware Fair India 2027 (23–25 October).
- INDIAWOOD 2027 is supported by the organizer homepage: 3–6 March at India Expo Mart & Centre, Greater Noida. Its automated source policy is DISALLOW based on site terms; this is manual evidence only.
- The official Indusfood schedule confirms the main Indusfood 2027 event on 8–10 January at India Expo Center & Mart. A separate existing row was corrected to Indusfood Manufacturing 2027 and left pending because its distinct edition details were not verified.
- EV India Expo 2027 is pending: the official page says 16–18 September while its FAQ says 16–17 September. The old June dates were recorded as unsupported. REI Expo 2027 is also pending: the home/contact pages and opening hours say 4–6 November, while a conference FAQ says 4–6 October.
- The official Corru Pack Print India page lists its next edition as 9–12 February 2028, so the unsupported 2027 date is marked out of the tracker horizon. Smart Home Expo's located 2027 announcement is Mumbai 13–15 May; no Delhi NCR 2027 edition was found, so the old November NCR date is retained only as an unconfirmed supplied date.
- BIRC 2027 official dates are TBA; the previous edition's 23–25 October 2026 dates remain only a planning reference. These unresolved records stay in Dates Pending.
- The evidence pass leaves 118 records marked `Evidence pending`, including 25 in Delhi NCR. The current workbook count is 87 on-schedule rows and 137 pending rows. The schedule includes the two corrected 2026 historical editions, each explicitly labelled historical in its audit note.
- The next workbook refinement should give completed editions a dedicated history view. Until that is added, Start Here and the audit notes clearly flag the two past 2026 rows in Events.


## Stage-wise plan

### Stage 1 — Make Source Health actionable

**Complete for the workbook pilot.** Crawl attempts and evidence references now have separate labels. Domain and registry state are visible, and the companion CSV groups records by domain. Current Source Health has 205 evidence links not scanned, nine blocked rows, 13 sources with event candidates and one successful empty scan. The 205 evidence links are research coverage gaps, not 205 crawl failures.

### Stage 2 — Expand official source coverage

**In progress.** The 26-source registry has 14 enabled sources, seven disallowed by policy, one access-blocked source and four under review. The 139 evidence domains outside the registry need source-by-source triage; unregistered domains are not automatically approved. Continue with the NCR queue above, then move to other metros and industries. Record the official calendar URL, robots/terms decision, collection method, delay and page limit. Prefer organizer, venue, trade-body and government sources.

### Stage 3 — Add extraction methods where they pay off

**Partly complete.** The current Python HTTP/HTML collector parses dated event-card links and public structured event data; the existing PDF path handles official calendars. The Gifts World scan now returns four city-edition links from one cached homepage. Medicall's scan exposed a stale 2020 structured event. ITPO needs an endpoint check: identify a public JSON or calendar endpoint from ordinary browser network requests first. Evaluate a browser fallback only for approved pages with no simpler endpoint; compare local Chrome/Edge WebDriver options against Playwright before selecting one. The dated-card behavior has a regression test.

### Stage 4 — Turn candidates into verified records

Deduplicate candidates by event, edition, city and year. Check organizer dates, venue, speaker or panel route, and key decision metrics. Eight pending dates were verified or corrected in this pass; 118 records remain marked `Evidence pending`, including 25 in Delhi NCR. Put unconfirmed editions in `Dates Pending`; promote only edition-backed records to `Events`. Preserve stable event IDs and shortlist marks.

### Stage 5 — Run the weekly local cycle

Run the scan manually on the laptop, review newly discovered and changed candidates, update verified JSON, and refresh the workbook after Excel is closed. Report new events, changed dates, failed sources, evidence gaps and sources needing manual review. Track coverage by domain and city so the 200+ scheduled-event goal reflects verified editions, not just discovered links.

### Stage 6 — Build the dashboard after the data loop works

Use the local Python dashboard to browse evidence, source health and shortlist marks. Move to React after Marketing and BD have used the workbook and the weekly data loop is stable. Keep the free, local operating path available.
