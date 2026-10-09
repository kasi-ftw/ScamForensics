from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def text_report(case_id, analysis, timeline, graph):
    lines = [
        "DIGITAL FORENSIC INVESTIGATION REPORT",
        "=" * 40,
        f"Case ID: {case_id}",
        f"Classification: {analysis['scam_type']}",
        f"Risk: {analysis['risk']} ({analysis['risk_score']}/100)",
        f"Campaign confidence: {analysis['campaign_confidence']}%",
        f"Evidence reviewed: {analysis['evidence_count']}",
        f"Connected evidence: {analysis['connected_evidence']}/{analysis['evidence_count']}",
        "", "ENTITY COUNTS",
    ]
    lines += [f"- {kind}: {count}" for kind, count in analysis["entity_counts"].items()]
    lines += ["", "TIMELINE"]
    lines += [f"- {item.get('timestamp') or 'Time not set'} | {item['kind']} | {item['filename']}" for item in timeline]
    lines += ["", "KEY FINDINGS"]
    lines += [f"- {item['label']} (+{item['points']})" for item in analysis["indicators"]]
    lines += ["", "SHARED IDENTIFIERS"]
    lines += [f"- {item['type']}: {item['value']} ({len(item['evidence_ids'])} artefacts)" for item in graph["shared_entities"]]
    lines += ["", "CONCLUSION", analysis["narrative"], "", "Disclaimer: These findings are automated indicators for investigator review, not legal conclusions."]
    return "\n".join(lines)


def pdf_report(text):
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    width, height = A4
    cursor = height - 48
    for line in text.splitlines():
        if cursor < 42:
            pdf.showPage(); cursor = height - 48
        pdf.drawString(42, cursor, line[:115])
        cursor -= 15
    pdf.save()
    output.seek(0)
    return output
