import os
import re
from urllib.parse import parse_qs, urlparse

PHONE_RE = re.compile(r"(?<!\d)(?:\+?91[-\s]?)?[6-9]\d{4}[-\s]?\d{5}(?!\d)")
URL_RE = re.compile(r"(?:(?:https?://)|(?:www\.))[\w.-]+(?:[/?#][^\s<>\"']*)?", re.I)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
UPI_RE = re.compile(r"\b[a-zA-Z0-9._-]{2,}@(?![a-zA-Z0-9.-]*\.)[a-zA-Z][a-zA-Z0-9_-]{1,}\b")
AMOUNT_RE = re.compile(r"(?:₹|Rs\.?|INR)\s?\d[\d,]*(?:\.\d{1,2})?", re.I)
TIME_RE = re.compile(r"\b(?:[01]?\d|2[0-3]):[0-5]\d(?:\s?[AP]M)?\b", re.I)

BANKS = ("SBI", "HDFC", "ICICI", "AXIS", "KOTAK", "PAYTM", "PHONEPE", "GOOGLE PAY")
KEYWORDS = ("kyc", "urgent", "blocked", "otp", "verify", "scan qr", "scan", "payment", "refund", "account suspended")
UPI_HANDLES = {"upi", "ybl", "oksbi", "okaxis", "okhdfcbank", "paytm", "ibl", "axl", "apl", "ptyes", "fbl"}


def _domain(url: str) -> str:
    candidate = url if "://" in url else "https://" + url
    return (urlparse(candidate).hostname or "").lower().removeprefix("www.")


def _add(found, kind, value):
    item = (kind, value)
    if value and item not in found:
        found.append(item)


def extract_entities(text: str):
    found = []
    for raw in PHONE_RE.findall(text):
        digits = re.sub(r"\D", "", raw)
        if len(digits) == 10:
            _add(found, "phone", "+91" + digits)
        elif len(digits) == 12 and digits.startswith("91"):
            _add(found, "phone", "+" + digits)
    for url in URL_RE.findall(text):
        _add(found, "url", _domain(url))
        if url.lower().startswith("upi://"):
            payload = parse_qs(urlparse(url).query)
            if payload.get("pa"):
                _add(found, "upi", payload["pa"][0].lower())
            _add(found, "qr", "QR referenced")
    # UPI URLs are not included in URL_RE by design, so parse them separately.
    for payload_url in re.findall(r"upi://pay\?[^\s<>\"']+", text, re.I):
        payload = parse_qs(urlparse(payload_url).query)
        if payload.get("pa"):
            _add(found, "upi", payload["pa"][0].lower())
        _add(found, "qr", "QR referenced")
    for value in EMAIL_RE.findall(text):
        _add(found, "email", value.lower())
    for value in UPI_RE.findall(text):
        handle = value.rsplit("@", 1)[1].lower()
        if handle in UPI_HANDLES or handle.startswith("ok"):
            _add(found, "upi", value.lower())
    for value in AMOUNT_RE.findall(text):
        _add(found, "amount", value.replace(" ", ""))
    lower = text.lower()
    for bank in BANKS:
        if bank.lower() in lower:
            _add(found, "organisation", bank)
    for word in KEYWORDS:
        if word in lower:
            _add(found, "keyword", word)
    for value in TIME_RE.findall(text):
        _add(found, "timestamp", value.upper().replace("  ", " "))
    return found


def infer_kind(filename: str, text: str) -> str:
    haystack = f"{filename} {text}".lower()
    if "upi://" in haystack or " qr" in haystack or "qr_" in haystack:
        return "qr"
    if any(x in haystack for x in ("payment", "paid", "transaction", "debited")):
        return "payment"
    if "whatsapp" in haystack:
        return "whatsapp"
    if "sms" in haystack:
        return "sms"
    if "email" in haystack or "subject:" in haystack:
        return "email"
    if URL_RE.search(text):
        return "url"
    return "text"


def optional_enrichment(text: str):
    """Reserved optional hook; failures never affect regex extraction."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return []
    return []
