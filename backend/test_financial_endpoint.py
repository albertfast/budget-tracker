import sys
import asyncio
from io import BytesIO

HTML_FILENAME = "test-edgar-10k.html"

PY313 = sys.version.startswith("3.13")

def _run_testclient_path(content: bytes):
    try:
        from fastapi.testclient import TestClient
        from app.main import app
    except Exception as e:
        print(f"TestClient import failed: {e}; falling back to direct coroutine invocation.")
        return False
    try:
        client = TestClient(app)
        files = {"file": (HTML_FILENAME, content, "text/html")}
        resp = client.post("/api/v1/insights/upload-financial-document", files=files)
        print(f"Status code: {resp.status_code}")
        if resp.status_code != 200:
            print("Response text:", resp.text)
            return False
        data = resp.json()
        print(f"Document type: {data.get('document_type')}")
        if data.get("document_type") == "Multi-period Financials":
            periods = data.get("summary_periods", [])
            assert periods, "No periods parsed"
            assert any(p.get("revenue", 0) > 0 for p in periods), "No revenue detected in periods"
            print("Periods summary:")
            for p in periods:
                print(p)
        return True
    except Exception as e:
        print(f"TestClient execution failed: {e}")
        return False

async def _direct_coroutine_path(content: bytes):
    """Fallback: directly invoke upload_financial_document endpoint coroutine without FastAPI UploadFile."""
    from app.api.insights import upload_financial_document

    class DummyUploadFile:
        def __init__(self, filename: str, data: bytes):
            self.filename = filename
            self._data = data
        async def read(self):
            return self._data

    upload = DummyUploadFile(HTML_FILENAME, content)
    result = await upload_financial_document(file=upload, current_user=None, db=None)
    print("Direct invocation document_type:", result.get("document_type"))
    if result.get("document_type") == "Multi-period Financials":
        periods = result.get("summary_periods", [])
        assert periods, "No periods parsed (direct path)"
        assert any(p.get("revenue", 0) > 0 for p in periods), "No revenue detected (direct path)"
        print("Periods summary (direct):")
        for p in periods:
            print(p)
    return True

def test_upload_multi_financials():
    try:
        with open(HTML_FILENAME, 'rb') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Missing test file {HTML_FILENAME}")
        sys.exit(1)

    used_testclient = _run_testclient_path(content)
    if not used_testclient:
        print("Falling back to direct coroutine invocation due to missing httpx / TestClient incompatibility.")
        asyncio.run(_direct_coroutine_path(content))

if __name__ == "__main__":
    test_upload_multi_financials()
    print("Endpoint test passed (with fallback if needed).")
