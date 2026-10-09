import os
from collections import Counter


def _llm_narrative(fallback, score, connected, total):
    """Use Anthropic only when explicitly configured; rule-based output is the fallback."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        return fallback
    try:
        from anthropic import Anthropic
        message = Anthropic().messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
            max_tokens=120,
            messages=[{"role": "user", "content": f"Summarise these non-legal scam indicators in two neutral sentences: risk score {score}/100, connected evidence {connected}/{total}. Say findings require investigator review."}],
        )
        return "".join(getattr(block, "text", "") for block in message.content).strip() or fallback
    except Exception:
        return fallback


def analyze(evidence, entities, graph):
    values = [(e["type"], e["value"]) for e in entities]
    text = " ".join(item["raw_text"] for item in evidence).lower()
    indicators, score = [], 0
    def add(points, title, present=True):
        nonlocal score
        if present:
            score += points
            indicators.append({"label": title, "points": points})
    urls = [v for t, v in values if t == "url"]
    listed_high_risk_domains = [v for t, v in values if t == "high_risk_domain"]
    impersonated = next((v for t, v in values if t == "organisation"), None)
    bank_match = (impersonated.lower() if impersonated else "")
    add(25, "Look-alike banking domain", bool(bank_match) and any(bank_match in d and any(w in d for w in ("kyc", "verify", "secure", "login")) for d in urls))
    add(35, "Domain on high-risk domain list", bool(listed_high_risk_domains))
    add(15, "KYC lure", "kyc" in text)
    add(10, "Urgency language", any(w in text for w in ("urgent", "blocked", "suspended", "immediately")))
    add(15, "Payment request", any(t == "amount" for t, _ in values) or "payment" in text)
    add(10, "QR payment request", any(t == "qr" for t, _ in values))
    add(5, "Phone number supplied", any(t == "phone" for t, _ in values))
    add(5, "Organisation impersonation", bool(impersonated))
    add(15, "Identifiers shared across evidence", bool(graph["shared_entities"]))
    score = min(score, 100)
    risk = "HIGH" if score >= 65 else "MEDIUM" if score >= 35 else "LOW"
    connected = len(graph["largest_cluster"])
    counts = dict(Counter(t for t, _ in values))
    confidence = round((connected / len(evidence) * 70 + min(score, 30)) if evidence and score else 0)
    scam_type = "No scam indicators detected" if score == 0 else ("Known high-risk domain" if listed_high_risk_domains else ("Fake bank KYC / payment scam" if "kyc" in text or impersonated else "Suspected digital scam"))
    fallback = f"{len(evidence)} artefacts were reviewed. {connected} are connected by shared identifiers; the combined indicators produce a {risk} risk assessment."
    narrative = _llm_narrative(fallback, score, connected, len(evidence))
    return {"scam_type": scam_type, "risk": risk, "risk_score": score, "campaign_confidence": min(confidence, 100), "impersonated_org": impersonated, "evidence_count": len(evidence), "connected_evidence": connected, "indicators": indicators, "entity_counts": counts, "narrative": narrative}
