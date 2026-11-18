"""Shared Excel formatting and the tracker planning views."""

import math
from datetime import date

from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.hyperlink import Hyperlink
from openpyxl.worksheet.table import Table, TableStyleInfo


PENDING_SHEET = "Dates Pending"
LEADERSHIP_SHEET = "Awards and CEO Opportunities"


def excel_date(value):
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return value


def format_table(sheet, name, widths, *, freeze="A2", hidden=(), links=(), shortlist=False, color="167D82"):
    sheet.sheet_view.showGridLines = False
    sheet.sheet_properties.tabColor = color
    sheet.freeze_panes = freeze
    sheet.sheet_view.zoomScale = 90
    sheet.row_dimensions[1].height = 31
    for index, width in enumerate(widths, 1):
        dimension = sheet.column_dimensions[get_column_letter(index)]
        dimension.width = width
        dimension.hidden = index in hidden
    for cell in sheet[1]:
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="17324D")
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row):
        lines = 1
        for cell in row:
            index = cell.column
            cell.font = Font(name="Arial", size=10, color="203349")
            cell.alignment = Alignment(vertical="center", wrap_text=index not in links)
            if cell.data_type == "f":
                cell.data_type = "s"
            if isinstance(cell.value, date):
                cell.number_format = "dd mmm yyyy"
            if index in links and isinstance(cell.value, str) and cell.value.startswith(("https://", "http://")):
                cell.hyperlink = cell.value
                cell.font = Font(name="Arial", size=10, color="086E80", underline="single")
            elif index not in hidden and isinstance(cell.value, str):
                lines = max(lines, math.ceil(len(cell.value) / max(1, widths[index - 1] - 3)))
        if row:
            sheet.row_dimensions[row[0].row].height = min(82, max(23, lines * 13 + 6))
    if sheet.max_row > 1:
        table = Table(displayName=name, ref=sheet.dimensions)
        table.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
        sheet.add_table(table)
    if shortlist and sheet.max_row > 1:
        region = f"B2:B{sheet.max_row}"
        validation = DataValidation(type="list", formula1='"Yes,No"', showErrorMessage=True)
        validation.error = "Choose Yes or No."
        sheet.add_data_validation(validation)
        validation.add(region)
        sheet.conditional_formatting.add(region, CellIsRule(operator="equal", formula=['"Yes"'],
                                                            fill=PatternFill("solid", fgColor="BDEBDD")))


def add_pending_sheet(workbook, events):
    sheet = workbook.create_sheet(PENDING_SHEET)
    sheet.append(["Event ID", "Shortlist", "Event", "City / lead location", "Region", "Evidence status",
                  "Planning window only", "Prior edition dates", "Prior edition source", "Source URL",
                  "Previously supplied date", "Review note", "Possible duplicate key"])
    for event in events:
        details = event["details"]
        sheet.append([event["event_id"], "Yes" if event["shortlisted"] else "No", event["name"], event["city"],
                      details.get("region"), details.get("audit_status", "Date pending"),
                      details.get("planning_window") or "No supported estimate", details.get("prior_dates"), details.get("prior_url"),
                      event["source_url"], excel_date(event["start_date"]), details.get("audit_note"),
                      details.get("possible_duplicate")])
    format_table(sheet, "PendingDates", [25, 12, 43, 22, 18, 25, 25, 22, 31, 31, 18, 59, 33],
                 freeze="D2", hidden=(1,), links=(9, 10), shortlist=True, color="B5822D")


def add_leadership_sheet(workbook, records, marks):
    sheet = workbook.create_sheet(LEADERSHIP_SHEET)
    sheet.append(["Opportunity ID", "Shortlist", "Opportunity", "Type", "Location", "Timing",
                  "Status", "AAJ angle", "Next action", "Organizer / source"])
    for record in records:
        sheet.append([record["id"], marks.get(record["id"], "No"), record["name"], record["type"],
                      record["location"], record["timing"], record["status"], record["fit"],
                      record["next_step"], record["source"]])
    format_table(sheet, "LeadershipOpportunities", [25, 12, 43, 23, 22, 34, 27, 55, 55, 35],
                 freeze="D2", hidden=(1,), links=(10,), shortlist=True, color="655195")


def add_navigation(workbook, counts):
    sheet = workbook.create_sheet("Start Here", 0)
    sheet.sheet_view.showGridLines = False
    sheet.sheet_properties.tabColor = "17324D"
    sheet.column_dimensions["A"].width = 5
    sheet.column_dimensions["B"].width = 38
    sheet.column_dimensions["C"].width = 11
    sheet.column_dimensions["D"].width = 80
    sheet["B2"] = "Event Tracker"
    sheet["B2"].font = Font(name="Arial", size=17, bold=True, color="17324D")
    sheet["B3"] = "November 2026 through December 2027"
    sheet["B3"].font = Font(name="Arial", size=10, color="51667C")
    sections = [
        ("Events", "Filter date-confirmed editions by date, region, industry or shortlist. Two completed 2026 editions remain for history and are flagged in their audit notes."),
        (PENDING_SHEET, "Use planning windows to decide when to check again. Prior editions and old supplied dates are shown separately."),
        ("Speaker Opportunities", "Filter by status. Check edition, deadline and eligibility before proposing a speaker."),
        (LEADERSHIP_SHEET, "Find awards, case competitions and CEO talks. Use Next action to follow up."),
        ("Source Health", "Review crawler outcomes and links to event sources."),
        ("Data Dictionary", "See what the shortlist and evidence labels mean."),
    ]
    for index, (name, description) in enumerate(sections, 6):
        link = sheet.cell(index, 2, name)
        link.hyperlink = Hyperlink(ref=link.coordinate, location=f"'{name}'!A1", display=name)
        link.font = Font(name="Arial", size=10, bold=True, color="086E80", underline="single")
        sheet.cell(index, 3, counts.get(name)).number_format = "0"
        sheet.cell(index, 4, description).alignment = Alignment(vertical="center", wrap_text=True)
        sheet.row_dimensions[index].height = 36
        for cell in sheet[index][1:4]:
            cell.fill = PatternFill("solid", fgColor="EAF2F6" if index % 2 == 0 else "F5F8FA")
    sheet["B13"] = "Shortlisting"
    sheet["B13"].font = Font(name="Arial", bold=True, color="17324D")
    sheet["D13"] = "Choose Yes in the Shortlist column. Save and close Excel before the weekly refresh."
    sheet["D13"].alignment = Alignment(wrap_text=True)
    sheet.row_dimensions[13].height = 30
    workbook.active = 0
