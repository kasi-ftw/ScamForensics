# Run ScamForensics

## Requirements

- Windows
- Python 3.10 or later
- Node.js 18 or later, including npm
- Tesseract OCR (optional; needed only to extract text from screenshots)

## First-time setup

Open PowerShell in this `scamforensics` folder, then run:

```powershell
Set-Location .\backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Set-Location ..\frontend
npm install
```

## Start the app

Double-click [run_scamforensics.bat](run_scamforensics.bat), or run this command from the `scamforensics` folder:

```powershell
.\run_scamforensics.bat
```

The launcher opens two command windows—one for the backend and one for the frontend—and then opens the app at [http://localhost:5173](http://localhost:5173).

## Start manually

If needed, open two PowerShell windows from the `scamforensics` folder.

In the first window, run:

```powershell
Set-Location .\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

In the second window, run:

```powershell
Set-Location .\frontend
npm run dev
```

Then open [http://localhost:5173](http://localhost:5173).

## Stop the app

Close the two command windows, or press `Ctrl+C` in each one.
