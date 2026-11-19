# Local directory capture design

The user wants a Python workflow for personally reviewing event listings from 10times and WHR.AI on their laptop. The public tracker must not publish raw directory data. The current local checks return HTTP 403 from a normal 10times request and redirect WHR event tools to sign-in.

Use a visible browser controlled by Playwright. The user completes any ordinary login or access step and navigates to a listing page. A keypress captures the current page's rendered HTML and extracts event-like links with a title and nearby date or location text. Save only unverified lead fields in `data/personal_capture/`, which Git ignores. Do not copy browser profiles, raw HTML or directory leads into the repository. Avoid automatic pagination, login handling, challenge solving, stealth, proxies and candidate promotion. The collector may capture multiple pages in one session and deduplicates by source URL.

Provide an offline `--html-file` mode for parser testing and a `--url` browser mode for live personal use. Only organizer-verified facts may later enter the public event seed and workbook through the existing review path. When a page is a sign-in or access-denied screen, report that no event cards were captured.
