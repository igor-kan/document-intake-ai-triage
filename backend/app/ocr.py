from __future__ import annotations

from io import BytesIO

from PIL import Image


def extract_text_with_confidence(image_bytes: bytes) -> tuple[str, float, str]:
    """
    Tries OCR extraction with pytesseract if available.
    Falls back gracefully when runtime/binary support is unavailable.
    """
    try:
        import pytesseract  # type: ignore

        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        text = pytesseract.image_to_string(image).strip()
        confidence = 0.82 if text else 0.35
        return text, confidence, "tesseract"
    except Exception:
        return "", 0.0, "unavailable"
