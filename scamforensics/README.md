# ScamForensics

ScamForensics is a hackathon MVP that turns disconnected scam artefacts into an explainable investigation: upload → OCR/text extraction → entity graph → timeline → campaign analysis → report.

It uses only fake demo data and produces **indicators for investigator review, not legal conclusions**.

## Run it

In one terminal:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite address (normally `http://localhost:5173`) and choose **Load demo case**. Tesseract is optional: images are accepted even if OCR is not installed, but they may have no readable text. No API key is required.

## Demo script

“What if an investigation has 20 pieces of evidence, not one?” Drag in a mix of chats, texts, email exports, QR screenshots, and payment notes. ScamForensics extracts repeated domains, phone numbers, UPI IDs, and emails; the graph highlights shared identifiers in red and groups connected artefacts as one campaign. Load the supplied six-artifact Fake SBI KYC case to show the expected HIGH-risk 6/6 connected result.

## Design notes

- FastAPI + plain `sqlite3`; evidence deletion cascades into entities.
- Regex extraction is the reliable baseline. `pytesseract` and an Anthropic key are intentionally optional, so the app degrades cleanly offline.
- Entity graphing uses union-find over shared phone/domain/UPI/email values. Keywords and generic QR mentions stay out of the graph.
- Risk scoring is rule-based, visible in the UI and report, and capped at 100.
- `/report` returns text and `/report.pdf` generates a reportlab PDF.

## Verify

```powershell
cd backend
pytest tests/test_smoke.py
cd ..\frontend
npm run build
```
