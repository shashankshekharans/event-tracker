# Event Tracker

A trade show lands in the marketing inbox. The audience looks right, the CEO could speak on fulfilment, and the venue is an hour from the office. Then someone notices the dates on the brochure are from last year.

**Event Tracker gives AAJ Supply Chain Management a calendar the team can question.** Open an event, see where its dates came from, and decide whether it deserves a visit, a stall, a speaker pitch or a case competition entry. Marketing and Business Development mark their picks in Excel. Management can filter the shortlist in the same file.

**[Download the populated workbook](docs/Event_Tracker.xlsx?raw=true)** · [Project plan](aaj_events.md) · [Developer handoff](AGENTS.md)

## Inside the workbook

The November 18, 2026 edition covers India through December 2027, with particular attention to Delhi NCR, warehousing, transport and e-commerce.

| Open this tab | When you want to… |
| --- | --- |
| Start Here | Jump straight to a working table. |
| Events | Browse 87 date-confirmed entries, including two completed 2026 editions retained for history. The audit marks 44 dates as organizer checked and retains 43 earlier verified entries. |
| Dates Pending | Follow 137 pending records. Nineteen have a planning window, including 15 with prior-edition dates. |
| Speaker Opportunities | Evaluate eight routes to a stage, including Delhi NCR panels and speaker nominations. |
| Awards and CEO Opportunities | Explore nine award, case competition and speaking leads, including CII SCALE, CII 5S and TEDxGateway. |
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

The [event records](data/verified_events.json), [speaker calls](data/speaker_opportunities.json) and [leadership opportunities](data/leadership_opportunities.json) feed the workbook. The latest evidence pass reduced the `Evidence pending` set from 127 to 118. Review the [source coverage audit](docs/source_coverage_audit_2026-11-18.md) and its [domain queue](docs/source_coverage_domains_2026-11-18.csv) before adding more sources. Reaching 200 scheduled events remains a research goal.

---

<div align="center">

### Made by Shashank

<a href="https://github.com/shashankshekharans"><img alt="GitHub: shashankshekharans" src="https://img.shields.io/badge/GitHub-shashankshekharans-24292f?logo=github&logoColor=white"></a>
<a href="https://www.instagram.com/shashankshekharans/"><img alt="Instagram: shashankshekharans" src="https://img.shields.io/badge/Instagram-shashankshekharans-c13584?logo=instagram&logoColor=white"></a>
<a href="https://x.com/SHASHANK_ANS"><img alt="X: SHASHANK_ANS" src="https://img.shields.io/badge/X-SHASHANK__ANS-000000?logo=x&logoColor=white"></a>

<sub>Built for AAJ Supply Chain Management with free tools. Python, SQLite, openpyxl and GitHub.</sub>

</div>
