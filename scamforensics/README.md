# How to use ScamForensics

ScamForensics helps you review scam-related evidence, connect shared details across items, assess risk, and create a report.

## Start the app

Open two terminals in the project folder.

In the first terminal, start the backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

In the second terminal, start the frontend:

```powershell
cd frontend
npm run dev
```

Open the address shown by Vite (normally [http://localhost:5173](http://localhost:5173)) in your browser.

## Investigate a case

1. Add your evidence in the left panel.
   - Drag files into the upload area to upload them.
   - Or paste message text into the text box and select **Add pasted evidence**.
2. Repeat for every message, email, URL, payment note, QR-code text, or other relevant item.
3. Select **INVESTIGATE** to analyze the case.
4. Review the dashboard:
   - **Campaign graph** shows evidence and the identifiers that connect it, such as phone numbers, UPI IDs, URLs, and domains. Items marked **SHARED** appear in more than one piece of evidence.
   - **Risk analysis** shows the risk level, score, connected evidence, confidence, and the indicators that contributed to the score.
   - **Timeline** places evidence in chronological order. For an item without a time, select **Set time** and enter one.
5. Select **Generate Report** to read the investigation summary. Choose **Download PDF** to save a PDF copy.

## Try the sample case

Select **Load demo case** to add the included example evidence. Then select **INVESTIGATE** and explore the graph, risk analysis, timeline, and report.

## Start over

Select **Clear** to remove the current evidence and begin a new case.

> ScamForensics provides automated indicators to support review. Treat its findings as investigative guidance, not a legal conclusion.
