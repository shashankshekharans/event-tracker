# Event Discovery and Speaker Opportunities — Design

## Intent

Expand the India event database through December 2027 so Marketing, Business Development, and management can shortlist both business-development events and events where AAJ leadership may apply to speak. The current 65-row workbook is a working seed, not a complete event census.

## Goals

- Discover more events from public event-listing directories, venue calendars, organizer calendars, associations, and government or embassy calendars.
- Keep the existing priority: NCR first, then Mumbai, Kolkata, Bengaluru, other metros, and Tier 2 cities; all industries remain in scope, with a slight B2B/B2C e-commerce preference.
- Treat listing sites as discovery sources. Verify the event edition, dates, location, and speaker-call claims from organizer or venue evidence whenever available.
- Make speaker calls independently searchable from exhibitor/attendee suitability. Include conferences and summits even when they have no exhibition floor.
- Preserve a free, local-first workflow. Manual discovery and source checking are acceptable when an automated route is unavailable or disallowed.

## Non-goals and constraints

- Do not bypass bot challenges, authentication, rate limits, or other access controls.
- Do not automate collection from sites whose terms prohibit it or use their content in ways their terms prohibit.
- Do not infer that an event is accepting speakers from prior-year speakers, a conference agenda, or the existence of a stage. Require a current call, official application route, or explicit organizer confirmation.
- No paid data subscriptions or APIs in this phase.

## Approaches considered

1. **Permitted-directory discovery with organizer verification — selected.** Use directories only where their access and reuse terms allow AAJ's internal business-planning use. Extract a candidate name, edition/year, city, and candidate URL; follow the organizer/venue page for validated facts. This broadens discovery without treating directory claims as authoritative.
2. **Paid event-intelligence provider.** Could provide wider event and speaker intelligence, but conflicts with the current no-additional-cost requirement.
3. **Automate all named directories regardless of terms.** Rejected. 10times' terms prohibit automated access and restrict use to personal, non-commercial purposes. Do not crawl it, import its event content, evade its controls, or add it to the enabled source registry unless AAJ obtains written permission that covers the intended use. WHR.ai is a paid product and is not enabled under the free constraint.

## Source handling

For every directory candidate, record the URL, publisher, access method, terms/robots review date, permitted-use outcome, and reason enabled or excluded. Only enable a source after the review supports the intended collection and internal use. Prefer public HTML, sitemaps, feeds, or downloadable calendars where permitted; use low request rates, caching, and bounded retries. No login/session scraping or CAPTCHA circumvention.

Use a directory listing to discover candidates, not as the only evidence for decision-critical facts. Preserve the listing URL as discovery provenance, then attach the official event URL and edition-specific source evidence. Keep conflicting, tentative, and missing dates visible rather than silently choosing one.

## Speaker opportunity information

Add a one-to-many `Speaker Opportunities` view keyed by immutable event-edition ID, plus a summary status in the Events sheet. Each opportunity row contains:

- Status: `OPEN`, `UPCOMING`, `CLOSED`, `UNKNOWN`, or `NOT_APPLICABLE`.
- A separate Yes/No shortlist mark for each speaker opportunity, independent of the event shortlist.
- Session type and topic/theme.
- Speaker eligibility or audience/role requirements where published.
- Call-for-speakers or application URL, deadline, and organizer contact where published.
- Evidence URL, last-checked date, and missing/conflicting information.

Use official organizer CFPs, conference programme pages, and explicit organizer confirmation as proof. A prior-year call or agenda can identify a lead to recheck, but cannot establish a current open opportunity. Initial topic discovery should cover AAJ-relevant leadership themes: supply chain and logistics, warehousing, fulfilment, e-commerce operations, 3PL, and logistics technology; the team can refine this list.

## Workbook and workflow

Keep the existing Events sheet and shortlist mark. Add a speaker-opportunity status/filter and a separate Speaker Opportunities sheet so several tracks or calls can be recorded for one event without duplicating event rows. The operator reviews directory candidates, confirms official sources, and refreshes the local workbook. The current plan's weekly manual cadence remains; automatic refresh is a later option for sources that permit it.

## Acceptance checks

- Candidate records identify their discovery source and organizer/venue verification source.
- Excluded sources such as 10times are not requested by the automatic collector and have an explicit exclusion reason.
- Speaker opportunities can be filtered separately from event suitability and shortlist status.
- No current speaking availability is marked `OPEN` without current official evidence.
- Dates, speaker deadlines, and source checks remain edition-specific and traceable.

## Sources checked for this design

- 10times Terms of Service, sections VII and VIII: https://10times.com/terms-of-service
- WHR.ai product and pricing information: https://whr.ai/
- Existing event scope and source strategy: `PRODUCT_PLAN.md`
