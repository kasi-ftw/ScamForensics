import os
import uuid
from io import BytesIO
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from . import db
from .analysis import analyze
from .extract import extract_entities, infer_kind
from .graph import build_graph
from .ocr import extract_image_text
from .report import pdf_report, text_report
from .timeline import build_timeline

app = FastAPI(title="ScamForensics", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
UPLOAD_DIR = Path(os.getenv("SCAMFORENSICS_UPLOAD_DIR", Path(__file__).resolve().parents[1] / "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

IMAGE_SUFFIXES = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp", "GIF": ".gif"}


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
        if item.get("file_path"):
            item["image_url"] = f"/api/uploads/{item['file_path']}"
    return evidence, entities


def add_evidence(filename: str, text: str, manual_timestamp: str | None = None, case_id: str = "CASE-DEMO", file_path: str | None = None):
    kind = infer_kind(filename, text)
    extracted = extract_entities(text)
    for domain in db.high_risk_domain_matches(text):
        if ("url", domain) not in extracted:
            extracted.append(("url", domain))
        extracted.append(("high_risk_domain", domain))
    timestamp = manual_timestamp or next((value for typ, value in extracted if typ == "timestamp"), None)
    source = "manual" if manual_timestamp else ("extracted" if timestamp else None)
    with db.connect() as conn:
        cursor = conn.execute("INSERT INTO evidence(case_id, filename, kind, raw_text, file_path, timestamp, ts_source) VALUES (?, ?, ?, ?, ?, ?, ?)", (case_id, filename, kind, text, file_path, timestamp, source))
        evidence_id = cursor.lastrowid
        conn.executemany("INSERT INTO entities(evidence_id, type, value) VALUES (?, ?, ?)", [(evidence_id, typ, value) for typ, value in extracted])
    return db.row("SELECT * FROM evidence WHERE id = ?", (evidence_id,))


def save_image(filename: str, data: bytes) -> str:
    try:
        image = Image.open(BytesIO(data))
        image_format = image.format
        image.verify()
    except (UnidentifiedImageError, OSError, SyntaxError) as error:
        raise HTTPException(415, "The uploaded file is not a valid image.") from error
    suffix = IMAGE_SUFFIXES.get(image_format or "")
    if not suffix:
        raise HTTPException(415, "Supported image formats are PNG, JPEG, WEBP, and GIF.")
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    (UPLOAD_DIR / stored_name).write_bytes(data)
    return stored_name


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
        stored_image = None
        if (file.filename or "").lower().endswith(".txt"):
            text = data.decode("utf-8", errors="replace")
        elif (file.content_type or "").startswith("image/") or (file.filename or "").lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            stored_image = save_image(file.filename or "image", data)
            text = extract_image_text(data)
            if not text:
                text = "[Image received; OCR unavailable or no readable text.]"
        else:
            text = data.decode("utf-8", errors="replace")
        created.append(add_evidence(file.filename or "upload", text, timestamp, case_id, stored_image))
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
    evidence, entities = evidence_with_entities()
    graph_data = build_graph(evidence, entities)
    result = analyze(evidence, entities, graph_data)
    case_id = evidence[0]["case_id"] if evidence else "CASE-DEMO"
    timeline = build_timeline(evidence)
    return StreamingResponse(
        pdf_report(case_id, result, timeline, graph_data, upload_dir=UPLOAD_DIR),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=ScamForensics-report.pdf"},
    )


def load_demo_case(directory: str, case_id: str):
    demo_dir = Path(__file__).resolve().parents[2] / "demo" / directory
    if not demo_dir.exists():
        raise HTTPException(500, "Demo evidence directory is missing")
    with db.connect() as conn:
        conn.execute("DELETE FROM evidence")
    created = []
    for file in sorted(demo_dir.glob("*.txt")):
        stored_image = None
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            matching_img = file.with_suffix(ext)
            if matching_img.exists():
                stored_name = f"{uuid.uuid4().hex}{ext}"
                (UPLOAD_DIR / stored_name).write_bytes(matching_img.read_bytes())
                stored_image = stored_name
                break
        created.append(add_evidence(file.name, file.read_text(encoding="utf-8"), case_id=case_id, file_path=stored_image))
    return {"loaded": len(created), "evidence": created}


@app.post("/demo/load")
def load_demo():
    return load_demo_case("evidence", "CASE-SBI-DEMO")


@app.post("/demo/load-safe")
def load_safe_demo():
    return load_demo_case("safe_evidence", "CASE-SAFE-DEMO")
