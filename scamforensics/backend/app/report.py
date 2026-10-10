import textwrap
from io import BytesIO
from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def _resolve_image_path(item, upload_dir=None):
    file_path = item.get("file_path")
    if file_path:
        cand = Path(file_path)
        if cand.is_file():
            return cand
        if upload_dir:
            cand_upload = Path(upload_dir) / file_path
            if cand_upload.is_file():
                return cand_upload
        default_upload = Path(__file__).resolve().parents[1] / "uploads" / file_path
        if default_upload.is_file():
            return default_upload

    # Check filename in upload directory or demo directories
    filename = item.get("filename", "")
    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
        if upload_dir:
            cand = Path(upload_dir) / filename
            if cand.is_file():
                return cand
        demo_evidence = Path(__file__).resolve().parents[2] / "demo" / "evidence" / filename
        if demo_evidence.is_file():
            return demo_evidence
        demo_safe = Path(__file__).resolve().parents[2] / "demo" / "safe_evidence" / filename
        if demo_safe.is_file():
            return demo_safe

    return None


def text_report(case_id, analysis, timeline, graph):
    lines = [
        "DIGITAL FORENSIC INVESTIGATION REPORT",
        "=" * 40,
        f"Case ID: {case_id}",
        f"Classification: {analysis.get('scam_type', 'N/A')}",
        f"Risk: {analysis.get('risk', 'UNKNOWN')} ({analysis.get('risk_score', 0)}/100)",
        f"Campaign confidence: {analysis.get('campaign_confidence', 0)}%",
        f"Evidence reviewed: {analysis.get('evidence_count', len(timeline))}",
        f"Connected evidence: {analysis.get('connected_evidence', 0)}/{analysis.get('evidence_count', len(timeline))}",
        "",
        "ENTITY COUNTS",
    ]
    lines += [f"- {kind}: {count}" for kind, count in analysis.get("entity_counts", {}).items()]
    lines += ["", "TIMELINE"]
    for item in timeline:
        time_str = item.get("timestamp") or "Time not set"
        if item.get("file_path") or item.get("image_url"):
            lines.append(f"- {time_str} | {item.get('kind', 'evidence')} | [Image artefact]")
        else:
            raw_preview = (item.get("raw_text") or "").strip().replace("\n", " ")
            if len(raw_preview) > 60:
                raw_preview = raw_preview[:57] + "..."
            lines.append(f"- {time_str} | {item.get('kind', 'evidence')} | {raw_preview or item.get('kind', 'evidence')}")
    lines += ["", "KEY FINDINGS"]
    lines += [f"- {item['label']} (+{item['points']})" for item in analysis.get("indicators", [])]
    lines += ["", "SHARED IDENTIFIERS"]
    lines += [f"- {item['type']}: {item['value']} ({len(item.get('evidence_ids', []))} artefacts)" for item in graph.get("shared_entities", [])]
    lines += [
        "",
        "CONCLUSION",
        analysis.get("narrative", ""),
        "",
        "Disclaimer: These findings are automated indicators for investigator review, not legal conclusions.",
    ]
    return "\n".join(lines)


def pdf_report(case_id_or_text, analysis=None, timeline=None, graph=None, upload_dir=None):
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    width, height = A4
    left = 42
    top = height - 48
    bottom = 45
    cursor = top

    def ensure_space(needed):
        nonlocal cursor
        if cursor - needed < bottom:
            pdf.showPage()
            cursor = top

    # Backward compatibility: if invoked with single text string argument
    if isinstance(case_id_or_text, str) and analysis is None:
        for line in case_id_or_text.splitlines():
            ensure_space(18)
            pdf.setFont("Helvetica", 9)
            pdf.setFillColor(colors.HexColor("#0f172a"))
            pdf.drawString(left, cursor, line[:115])
            cursor -= 15
        pdf.save()
        output.seek(0)
        return output

    case_id = case_id_or_text
    analysis = analysis or {}
    timeline = timeline or []
    graph = graph or {"shared_entities": []}

    # 1. Header & Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColor(colors.HexColor("#0f172a"))
    pdf.drawString(left, cursor, "DIGITAL FORENSIC INVESTIGATION REPORT")
    cursor -= 16

    pdf.setStrokeColor(colors.HexColor("#334155"))
    pdf.setLineWidth(1.5)
    pdf.line(left, cursor, width - left, cursor)
    cursor -= 18

    # 2. Executive Summary Block
    pdf.setFont("Helvetica-Bold", 10)
    pdf.setFillColor(colors.HexColor("#0f172a"))
    pdf.drawString(left, cursor, f"Case ID: {case_id}")
    cursor -= 14

    pdf.setFont("Helvetica", 9.5)
    pdf.setFillColor(colors.HexColor("#1e293b"))
    pdf.drawString(left, cursor, f"Classification: {analysis.get('scam_type', 'N/A')}")
    cursor -= 13

    risk = analysis.get("risk", "UNKNOWN")
    risk_score = analysis.get("risk_score", 0)
    pdf.drawString(left, cursor, f"Risk Assessment: {risk} ({risk_score}/100)")
    cursor -= 13

    confidence = analysis.get("campaign_confidence", 0)
    pdf.drawString(left, cursor, f"Campaign Confidence: {confidence}%")
    cursor -= 13

    ev_count = analysis.get("evidence_count", len(timeline))
    conn_count = analysis.get("connected_evidence", 0)
    pdf.drawString(left, cursor, f"Evidence Reviewed: {ev_count}  |  Connected Artefacts: {conn_count}/{ev_count}")
    cursor -= 13

    if analysis.get("impersonated_org"):
        pdf.drawString(left, cursor, f"Impersonated Organisation: {analysis['impersonated_org']}")
        cursor -= 13

    cursor -= 8

    # 3. Entity Counts
    ensure_space(35)
    pdf.setFont("Helvetica-Bold", 10.5)
    pdf.setFillColor(colors.HexColor("#0f172a"))
    pdf.drawString(left, cursor, "ENTITY COUNTS")
    cursor -= 14

    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(colors.HexColor("#334155"))
    counts = analysis.get("entity_counts", {})
    if counts:
        for kind, count in counts.items():
            ensure_space(14)
            pdf.drawString(left + 12, cursor, f"• {kind}: {count}")
            cursor -= 13
    else:
        pdf.drawString(left + 12, cursor, "• No entities detected")
        cursor -= 13

    cursor -= 8

    # 4. Key Findings (Indicators)
    ensure_space(35)
    pdf.setFont("Helvetica-Bold", 10.5)
    pdf.setFillColor(colors.HexColor("#0f172a"))
    pdf.drawString(left, cursor, "KEY FINDINGS")
    cursor -= 14

    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(colors.HexColor("#334155"))
    indicators = analysis.get("indicators", [])
    if indicators:
        for item in indicators:
            ensure_space(14)
            pdf.drawString(left + 12, cursor, f"• {item['label']} (+{item['points']} pts)")
            cursor -= 13
    else:
        pdf.drawString(left + 12, cursor, "• No suspicious indicators detected")
        cursor -= 13

    cursor -= 8

    # 5. Shared Identifiers
    ensure_space(35)
    pdf.setFont("Helvetica-Bold", 10.5)
    pdf.setFillColor(colors.HexColor("#0f172a"))
    pdf.drawString(left, cursor, "SHARED IDENTIFIERS")
    cursor -= 14

    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(colors.HexColor("#334155"))
    shared = graph.get("shared_entities", [])
    if shared:
        for item in shared:
            ensure_space(14)
            count_art = len(item.get("evidence_ids", []))
            pdf.drawString(left + 12, cursor, f"• {item['type']}: {item['value']} ({count_art} artefacts)")
            cursor -= 13
    else:
        pdf.drawString(left + 12, cursor, "• No shared cross-artefact identifiers")
        cursor -= 13

    cursor -= 10

    # 6. Timeline & Evidence Artefacts (IMAGES INSTEAD OF FILENAME!)
    ensure_space(45)
    pdf.setFont("Helvetica-Bold", 10.5)
    pdf.setFillColor(colors.HexColor("#0f172a"))
    pdf.drawString(left, cursor, "TIMELINE & EVIDENCE")
    cursor -= 16

    for item in timeline:
        time_val = item.get("timestamp") or "Time not set"
        kind_val = (item.get("kind") or "evidence").upper()
        img_path = _resolve_image_path(item, upload_dir)

        if img_path:
            # Render item header without file name
            ensure_space(40)
            pdf.setFont("Helvetica-Bold", 9)
            pdf.setFillColor(colors.HexColor("#0f172a"))
            pdf.drawString(left + 8, cursor, f"• {time_val}  |  {kind_val}")
            cursor -= 14

            try:
                pil_img = Image.open(img_path)
                orig_w, orig_h = pil_img.size
                max_w = min(width - 2 * left - 30, 360)
                max_h = 220
                scale = min(max_w / orig_w, max_h / orig_h)
                disp_w = orig_w * scale
                disp_h = orig_h * scale

                ensure_space(disp_h + 20)
                img_x = left + 16
                img_y = cursor - disp_h

                if pil_img.mode in ("RGBA", "LA") or (pil_img.mode == "P" and "transparency" in pil_img.info):
                    bg = Image.new("RGB", pil_img.size, (255, 255, 255))
                    rgba = pil_img.convert("RGBA")
                    bg.paste(rgba, mask=rgba.split()[-1])
                    ir = ImageReader(bg)
                else:
                    ir = ImageReader(pil_img.convert("RGB"))

                pdf.drawImage(ir, img_x, img_y, width=disp_w, height=disp_h)
                pdf.setStrokeColor(colors.HexColor("#cbd5e1"))
                pdf.setLineWidth(0.75)
                pdf.rect(img_x, img_y, disp_w, disp_h, stroke=1, fill=0)
                cursor = img_y - 14
            except Exception as error:
                ensure_space(14)
                pdf.setFont("Helvetica-Oblique", 9)
                pdf.setFillColor(colors.HexColor("#64748b"))
                pdf.drawString(left + 16, cursor, f"[Image display error: {str(error)[:50]}]")
                cursor -= 14
        else:
            # Pure text / message artefact
            ensure_space(26)
            pdf.setFont("Helvetica-Bold", 9)
            pdf.setFillColor(colors.HexColor("#0f172a"))
            raw_preview = (item.get("raw_text") or "").strip().replace("\n", " ")
            if len(raw_preview) > 75:
                raw_preview = raw_preview[:72] + "..."
            pdf.drawString(left + 8, cursor, f"• {time_val}  |  {kind_val}  |  {raw_preview}")
            cursor -= 14

    cursor -= 10

    # 7. Conclusion & Narrative
    ensure_space(50)
    pdf.setFont("Helvetica-Bold", 10.5)
    pdf.setFillColor(colors.HexColor("#0f172a"))
    pdf.drawString(left, cursor, "CONCLUSION")
    cursor -= 14

    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(colors.HexColor("#334155"))
    narrative = analysis.get("narrative", "")
    for line in textwrap.wrap(narrative, width=95):
        ensure_space(14)
        pdf.drawString(left + 12, cursor, line)
        cursor -= 13

    cursor -= 12
    ensure_space(25)
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.setFillColor(colors.HexColor("#64748b"))
    pdf.drawString(left, cursor, "Disclaimer: These findings are automated indicators for investigator review, not legal conclusions.")

    pdf.save()
    output.seek(0)
    return output
