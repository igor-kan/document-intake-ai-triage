from pathlib import Path

HIGH_PRIORITY_HINTS = {"urgent", "appeal", "deadline", "escalation"}


def infer_document_type(filename: str, content_type: str) -> str:
    name = filename.lower()
    if name.endswith((".png", ".jpg", ".jpeg", ".tiff")):
        return "scanned_form"
    if name.endswith(".pdf"):
        return "pdf_form"
    if "spreadsheet" in content_type or name.endswith((".csv", ".xlsx")):
        return "tabular_data"
    if name.endswith((".json", ".xml")):
        return "structured_payload"
    return "unknown"


def infer_priority(filename: str) -> str:
    lowered = Path(filename).stem.lower()
    if any(term in lowered for term in HIGH_PRIORITY_HINTS):
        return "high"
    return "normal"
