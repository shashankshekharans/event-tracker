# Event Tracker

A promising event lands in your inbox. The audience looks right. The venue is within reach. There might even be a stage for your next big idea. You are ready to put it on the calendar - until someone notices the brochure is from last year.

**Event Tracker turns that moment of doubt into a better decision.** It gives anyone researching events a calendar they can question: open a listing, follow its dates to the source and decide whether it deserves a visit, a stall, a speaker pitch or a case competition entry. Mark the promising ones in Excel and share a shortlist others can inspect for themselves.

**[Download the populated workbook](docs/Event_Tracker.xlsx?raw=true)** · [Project plan](PRODUCT_PLAN.md) · [Developer handoff](AGENTS.md)

## Inside the workbook

The November 19, 2026 edition covers India through December 2027, with particular attention to Delhi NCR, warehousing, transport and e-commerce.

| Open this tab | When you want to… |
| --- | --- |
| Start Here | Jump straight to a working table. |
| Events | Browse 96 date-confirmed entries, including two completed 2026 editions retained for history. The audit marks 53 dates as organizer checked and retains 43 earlier verified entries. |
| Dates Pending | Follow 137 pending records. Nineteen have a planning window, including 15 with prior-edition dates. |
| Speaker Opportunities | Evaluate eight routes to a stage, including Delhi NCR panels and speaker nominations. |
| Awards and CEO Opportunities | Explore ten award, case competition and speaking leads, including CII SCALE, FICCI Road Safety Awards, CII 5S and TEDxGateway. |
| Source Health and Data Dictionary | Separate crawl outcomes from evidence links that have not been scanned; filter by domain and registry state. |

A practical first move is to filter **Events** to Delhi NCR, open an organizer link, then set **Shortlist** to **Yes**. A speaking opportunity has its own mark, so the team can pursue a panel even when it passes on an exhibition stall.

## Run your weekly working copy

The download above is a preview. For a working copy that keeps shortlist marks across refreshes, generate the workbook and its matching SQLite database together. From the repository root on Windows with Python 3.12 installed:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m tracker.cli refresh
.\.venv\Scripts\python -m tracker.cli status
```

Open **data/Event_Tracker.xlsx**. Save and close it before each refresh. Refresh reads your shortlist marks, writes a previous-workbook backup and rebuilds the tables. Keep the working workbook and **data/events.sqlite** together when moving between computers.

## Find the next event

Run `python -m tracker.cli scan` in the installed environment to discover leads from enabled sources in [the registry](config/source_pages.json). The collector records where each link came from. Verify the edition, city and dates against the organizer before promoting a lead to the schedule. When a date is pending, a sourced prior edition can support a planning month.

For a separate personal research pass on directory pages you open yourself, install the optional browser package and launch the local capture tool:

```powershell
.\.venv\Scripts\python -m pip install -r requirements-personal.txt
.\.venv\Scripts\python -m tracker.personal_capture --site 10times --url https://10times.com/newdelhi-in/tradeshows
.\.venv\Scripts\python -m tracker.personal_capture --site whr --url https://gtm.whr.ai/
```

The script opens visible Chrome and waits for you to navigate. Sign in to WHR with your own account if needed. Press Enter to capture each listing page and `q` to finish. It saves dated links and its browser profile only under ignored `data/personal_capture/`. You can also save a page there and pass `--html-file data/personal_capture/page.html --page-url <original-url>` for offline extraction. A direct browser check reached a 10times challenge and a WHR sign-in page; the tool does not work around either. Captured links are unverified leads, so check the organizer before adding an event to the public tracker.

The [event records](data/verified_events.json), [speaker calls](data/speaker_opportunities.json) and [leadership opportunities](data/leadership_opportunities.json) feed the workbook. The latest evidence pass reduced the `Evidence pending` set from 127 to 118. India ITME 2026 and eight events from FICCI's current calendar were added from organizer-published facts. The FICCI scan staged 38 candidate links; eight became verified event records, while the others still need review or rejection. Check the [source coverage audit](docs/source_coverage_audit_2026-11-18.md), its [domain queue](docs/source_coverage_domains_2026-11-18.csv) and the [source expansion notes](docs/source_expansion_2026-11-19.md) before adding more sources. Reaching 200 scheduled events remains a research goal.

---

<div align="center">

### Made by Shashank

<a href="https://github.com/shashankshekharans"><img alt="GitHub: shashankshekharans" src="https://img.shields.io/badge/GitHub-shashankshekharans-24292f?logo=github&logoColor=white"></a>
<a href="https://www.instagram.com/shashankshekharans/"><img alt="Instagram: shashankshekharans" src="https://img.shields.io/badge/Instagram-shashankshekharans-c13584?logo=instagram&logoColor=white"></a>
<a href="https://x.com/SHASHANK_ANS"><img alt="X: SHASHANK_ANS" src="https://img.shields.io/badge/X-SHASHANK__ANS-000000?logo=x&logoColor=white"></a>

<sub>Built for curious teams and independent researchers with free tools: Python, SQLite, openpyxl and GitHub.</sub>

</div>
