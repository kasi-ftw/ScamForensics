import os
import tempfile
from io import BytesIO

from PIL import Image

os.environ["SCAMFORENSICS_DB"] = os.path.join(tempfile.gettempdir(), "scamforensics-smoke.db")
os.environ["SCAMFORENSICS_UPLOAD_DIR"] = os.path.join(tempfile.gettempdir(), "scamforensics-smoke-uploads")
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


def test_high_risk_domain_list_is_checked():
    with TestClient(app) as client:
        response = client.post("/upload", data={"pasted_text": "Review https://alchemygp.vip/login before investing."})
        assert response.status_code == 200
        output = client.post("/analyze").json()
        assert output["analysis"]["scam_type"] == "Known high-risk domain"
        assert any(item["label"] == "Domain on high-risk domain list" for item in output["analysis"]["indicators"])


def test_png_upload_is_saved_and_available():
    image_buffer = BytesIO()
    Image.new("RGB", (2, 2), color="white").save(image_buffer, format="PNG")
    with TestClient(app) as client:
        response = client.post("/upload", files={"files": ("screenshot.png", image_buffer.getvalue(), "image/png")})
        assert response.status_code == 200
        evidence = client.get("/evidence").json()[-1]
        assert evidence["filename"] == "screenshot.png"
        assert evidence["image_url"].startswith("/api/uploads/")
        assert client.get(evidence["image_url"].removeprefix("/api")).status_code == 200

        # Verify text report does not expose raw filename in timeline
        txt_report = client.get("/report").text
        assert "screenshot.png" not in txt_report
        assert "[Image artefact]" in txt_report

        # Verify PDF report generation succeeds with image embedded
        pdf_res = client.get("/report.pdf")
        assert pdf_res.status_code == 200
        assert pdf_res.headers["content-type"] == "application/pdf"
        assert len(pdf_res.content) > 1000
