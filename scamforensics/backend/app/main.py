from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse

from . import db
from .analysis import analyze
from .extract import extract_entities, infer_kind
from .graph import build_graph
from .ocr import extract_image_text
from .report import pdf_report, text_report
from .timeline import build_timeline

app = FastAPI(title="ScamForensics", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def startup():
    db.init_db()


def evidence_with_entities():
    evidence = db.rows("SELECT * FROM evidence ORDER BY id")
    entities = db.rows("SELECT * FROM entities ORDER BY id")
    attached = {}
    for item in entities:
        attached.setdefault(item["evidence_id"], []).append(item)
    for item in evidence:
        item["entities"] = attached.get(item["id"], [])
    return evidence, entities


def add_evidence(filename: str, text: str, manual_timestamp: str | None = None, case_id: str = "CASE-DEMO"):
    kind = infer_kind(filename, text)
    extracted = extract_entities(text)
    timestamp = manual_timestamp or next((value for typ, value in extracted if typ == "timestamp"), None)
    source = "manual" if manual_timestamp else ("extracted" if timestamp else None)
    with db.connect() as conn:
        cursor = conn.execute("INSERT INTO evidence(case_id, filename, kind, raw_text, timestamp, ts_source) VALUES (?, ?, ?, ?, ?, ?)", (case_id, filename, kind, text, timestamp, source))
        evidence_id = cursor.lastrowid
        conn.executemany("INSERT INTO entities(evidence_id, type, value) VALUES (?, ?, ?)", [(evidence_id, typ, value) for typ, value in extracted])
    return db.row("SELECT * FROM evidence WHERE id = ?", (evidence_id,))


@app.get("/health")
def health():
    return {"status": "ok", "service": "ScamForensics"}


@app.post("/upload")
async def upload(
    files: Annotated[list[UploadFile] | None, File()] = None,
    pasted_text: Annotated[str | None, Form()] = None,
    timestamp: Annotated[str | None, Form()] = None,
    case_id: Annotated[str, Form()] = "CASE-DEMO",
):
    created = []
    for file in files or []:
        data = await file.read()
        if (file.filename or "").lower().endswith(".txt"):
            text = data.decode("utf-8", errors="replace")
        elif (file.content_type or "").startswith("image/"):
            text = extract_image_text(data)
            if not text:
                text = "[Image received; OCR unavailable or no readable text.]"
        else:
            text = data.decode("utf-8", errors="replace")
        created.append(add_evidence(file.filename or "upload", text, timestamp, case_id))
    if pasted_text and pasted_text.strip():
        created.append(add_evidence("pasted-text", pasted_text.strip(), timestamp, case_id))
    if not created:
        raise HTTPException(400, "Provide one or more files or pasted text.")
    return {"created": created, "count": len(created)}


@app.get("/evidence")
def get_evidence():
    return evidence_with_entities()[0]


@app.get("/entities")
def get_entities():
    return evidence_with_entities()[1]


@app.patch("/evidence/{evidence_id}/timestamp")
def set_timestamp(evidence_id: int, body: dict):
    timestamp = body.get("timestamp")
    if not timestamp:
        raise HTTPException(400, "timestamp is required")
    with db.connect() as conn:
        cursor = conn.execute("UPDATE evidence SET timestamp = ?, ts_source = 'manual' WHERE id = ?", (timestamp, evidence_id))
        if not cursor.rowcount:
            raise HTTPException(404, "Evidence not found")
    return db.row("SELECT * FROM evidence WHERE id = ?", (evidence_id,))


@app.delete("/evidence")
def clear_evidence():
    with db.connect() as conn:
        conn.execute("DELETE FROM evidence")
    return {"cleared": True}


@app.get("/graph")
def graph():
    evidence, entities = evidence_with_entities()
    return build_graph(evidence, entities)


@app.get("/timeline")
def timeline():
    return build_timeline(evidence_with_entities()[0])


@app.post("/analyze")
def run_analysis():
    evidence, entities = evidence_with_entities()
    graph_data = build_graph(evidence, entities)
    return {"analysis": analyze(evidence, entities, graph_data), "graph": graph_data, "timeline": build_timeline(evidence)}


def report_data():
    evidence, entities = evidence_with_entities()
    graph_data = build_graph(evidence, entities)
    result = analyze(evidence, entities, graph_data)
    case_id = evidence[0]["case_id"] if evidence else "CASE-DEMO"
    return text_report(case_id, result, build_timeline(evidence), graph_data)


@app.get("/report", response_class=PlainTextResponse)
def report():
    return report_data()


@app.get("/report.pdf")
def report_pdf():
    return StreamingResponse(pdf_report(report_data()), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=ScamForensics-report.pdf"})


@app.post("/demo/load")
def load_demo():
    demo_dir = Path(__file__).resolve().parents[2] / "demo" / "evidence"
    if not demo_dir.exists():
        raise HTTPException(500, "Demo evidence directory is missing")
    with db.connect() as conn:
        conn.execute("DELETE FROM evidence")
    created = [add_evidence(file.name, file.read_text(encoding="utf-8"), case_id="CASE-SBI-DEMO") for file in sorted(demo_dir.glob("*.txt"))]
    return {"loaded": len(created), "evidence": created}
