import time

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_triage_policy_and_confidence(client: TestClient) -> None:
    response = client.post(
        "/api/intake/triage",
        files={"file": ("urgent-report.csv", b"a,b\n1,2", "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["document_type"] == "tabular_data"
    assert body["priority"] == "high"
    assert body["policy"]["route_queue"] == "data_ingest"
    assert body["confidence"]["classification"] > 0.8


def test_batch_queue_and_review_flow(client: TestClient) -> None:
    submit = client.post(
        "/api/intake/batch/submit",
        json={
            "documents": [
                {
                    "filename": "appeal-permit.pdf",
                    "content_type": "application/pdf",
                    "text_hint": "urgent deadline appeal"
                },
                {
                    "filename": "dataset.csv",
                    "content_type": "text/csv",
                    "text_hint": "tabular payload"
                }
            ]
        },
    )
    assert submit.status_code == 200
    job_id = submit.json()["job_id"]

    job = None
    for _ in range(20):
        time.sleep(0.1)
        status = client.get(f"/api/intake/jobs/{job_id}")
        assert status.status_code == 200
        job = status.json()
        if job["status"] == "completed":
            break

    assert job is not None
    assert job["status"] == "completed"
    assert len(job["results"]) == 2

    review = client.post(
        f"/api/intake/jobs/{job_id}/review",
        json={
            "document_index": 0,
            "corrected_document_type": "pdf_form",
            "corrected_priority": "high",
            "notes": "Manual reviewer confirmed PDF appeal document"
        },
    )
    assert review.status_code == 200
    reviewed = review.json()
    assert reviewed["result"]["document_type"] == "pdf_form"
    assert reviewed["result"]["human_review"]["applied"] is True
