import os
import tempfile

os.environ["SCAMFORENSICS_DB"] = os.path.join(tempfile.gettempdir(), "scamforensics-smoke.db")
try:
    os.remove(os.environ["SCAMFORENSICS_DB"])
except FileNotFoundError:
    pass

from fastapi.testclient import TestClient
from app.main import app


def test_upload_and_analyze():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        response = client.post("/upload", data={"pasted_text": "SBI KYC urgent: visit https://sbi-kyc-verify-example.com and pay Rs 25,000 to fraudtest@ybl. Call 98765 43210 at 10:21 AM."})
        assert response.status_code == 200
        output = client.post("/analyze").json()
        assert output["analysis"]["risk_score"] >= 65
        assert output["graph"]["nodes"]


def test_safe_demo_is_low_risk():
    with TestClient(app) as client:
        response = client.post("/demo/load-safe")
        assert response.status_code == 200
        output = client.post("/analyze").json()
        assert output["analysis"]["risk"] == "LOW"
        assert output["analysis"]["risk_score"] == 0
        assert output["analysis"]["scam_type"] == "No scam indicators detected"
