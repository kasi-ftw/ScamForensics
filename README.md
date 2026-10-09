# ScamForensics

*OPCODE IMPACT 2026 | Hackathon Submission*

*Team ID:* OPCO24

## 1. Problem Statement

Digital-scam evidence is often scattered across screenshots, WhatsApp messages, SMS, emails, URLs, QR codes, and payment records. Reviewing these artefacts separately makes it difficult to identify common identifiers, reconstruct the incident, and present findings clearly.

## 2. Solution Title

ScamForensics: Explainable Digital Scam Investigation Platform

## 3. Solution Description

ScamForensics brings scam-related evidence into one investigation workspace. It uses local OCR to read uploaded screenshots and extracts key indicators such as Indian phone numbers, UPI IDs, email addresses, URLs, bank names, payment amounts, and timestamps. Shared identifiers connect artefacts in an interactive graph, while rule-based analysis produces an explainable risk score and timeline. Investigators can then generate a plain-text or PDF report of the case findings.

## 4. Architecture Diagram

![Architecture Diagram](docs/architecture.png)

Evidence is uploaded from the React dashboard as text files, pasted text, or screenshots. FastAPI uses OCR and rule-based extraction to store evidence and identifiers in SQLite, then correlates matching identifiers into a campaign graph. The dashboard displays the graph, timeline, and risk assessment; ReportLab exports the investigation report as a PDF.

## 5. Technology Stack

- *Frontend:* React, Vite, Tailwind CSS, React Flow
- *Backend:* Python, FastAPI, Uvicorn
- *Database:* SQLite
- *Other Technologies:* Tesseract OCR via Pytesseract, Pillow, ReportLab, optional Anthropic API narrative generation

## 6. Quick Start Guide

*Prerequisites:* Windows, Python 3.10 or later, Node.js 18 or later, and npm. Install Tesseract OCR separately if screenshot text extraction is required.

*Installation & Execution:*

```powershell
# Run once from the Opcode project folder
Set-Location .\scamforensics\backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Set-Location ..\frontend
npm install

# Run the app
Set-Location ..
.\run_scamforensics.bat
```

The launcher starts the backend and frontend in separate terminals, then opens `http://localhost:5173` in your browser.

## 7. Output Screenshots

![Output Screenshot](docs/output.png)

The dashboard shows uploaded evidence, an identifier-relationship graph, risk indicators and score, a chronological timeline, and an option to download the investigation report as a PDF.

## 8. Future Scope

- Add fuzzy matching to identify similar UPI IDs, domains, and scam patterns instead of only exact shared identifiers.
- Integrate live reputation and threat-intelligence services for URLs, phone numbers, and domains.
- Support multilingual OCR and improved image preprocessing for lower-quality screenshots.
- Add case accounts, evidence auditing, and controlled collaboration for investigation teams.

## 9. Team Contributions

| Member Name | Contribution |
|-------------|--------------|
| Kasinath Remesh | [Work completed] |
| Anju V Mohanan | [Work completed] |
| Meenakshi Krishnakumar | [Work completed] |

## 10. Tools Used

| Tool / Platform | Purpose / Why Used |
|-----------------|--------------------|
| React, Vite, and Tailwind CSS | Build a fast, responsive dashboard for evidence intake and investigation views. |
| FastAPI and Python | Provide the API, OCR pipeline, entity extraction, risk analysis, and report generation. |
| SQLite | Store evidence records and extracted identifiers locally. |
| Tesseract OCR, Pytesseract, and Pillow | Extract readable text from uploaded screenshots. |
| React Flow | Visualize relationships between evidence and shared identifiers. |
| ReportLab | Generate downloadable PDF investigation reports. |
| Anthropic API (optional) | Generate a concise narrative summary when an API key is configured. |
