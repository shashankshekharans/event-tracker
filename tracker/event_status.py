"""Evidence rules shared by the workbook and local store."""

SCHEDULED = {"Organizer date checked", "Previously recorded"}


def is_scheduled(event):
    if not event["start_date"]:
        return False
    details = event["details"]
    audit_status = details.get("audit_status")
    if audit_status == "Organizer date checked":
        return True
    certainty = str(details.get("date_certainty") or "").casefold()
    uncertain = any(term in certainty for term in ("tentative", "provisional", "not announced", "conflicting"))
    return not uncertain and (audit_status is None or audit_status in SCHEDULED)
