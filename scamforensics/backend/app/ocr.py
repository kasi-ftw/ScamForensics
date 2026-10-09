"""Best-effort OCR. Imports stay optional so the API works without Tesseract."""
from io import BytesIO


def extract_image_text(data: bytes) -> str:
    try:
        from PIL import Image
        import pytesseract

        return pytesseract.image_to_string(Image.open(BytesIO(data))).strip()
    except Exception:
        return ""
