from datetime import datetime

FLOW_ORDER = {"whatsapp": 0, "sms": 0, "email": 0, "url": 1, "qr": 2, "payment": 3, "text": 4}


def _time(value):
    if not value:
        return None
    for pattern in ("%I:%M %p", "%H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(value.upper(), pattern)
        except ValueError:
            pass
    return None


def build_timeline(evidence):
    def key(item):
        parsed = _time(item.get("timestamp"))
        return (0, parsed, FLOW_ORDER.get(item["kind"], 9), item["id"]) if parsed else (1, datetime.max, FLOW_ORDER.get(item["kind"], 9), item["id"])
    return sorted(evidence, key=key)
