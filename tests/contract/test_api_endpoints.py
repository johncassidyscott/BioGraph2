import pytest
from fastapi.testclient import TestClient
from biograph.api.main import app

client = TestClient(app)

def test_get_issuers():
    response = client.get("/api/v1/issuers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_issuer():
    # Use a known CIK from your data
    response = client.get("/api/v1/issuers/CIK_0000001800")
    assert response.status_code == 200
    assert "issuer_id" in response.json()

def test_get_filings():
    response = client.get("/api/v1/issuers/CIK_0000001800/filings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
