# Phase 2 Delivery

Implemented in this repository:

1. OCR integration + confidence scoring
- Optional Tesseract OCR hook with graceful fallback.
- Confidence block includes classification, OCR, and overall confidence.

2. Queue-backed async processing
- In-memory queue and background worker for batch triage jobs.
- Endpoints:
  - `POST /api/intake/batch/submit`
  - `GET /api/intake/jobs/{job_id}`

3. Human-in-the-loop review
- Endpoint: `POST /api/intake/jobs/{job_id}/review`
- Applies reviewer corrections to selected document result.

4. Policy/plugin routing by document type
- Policy resolver maps document types to queue, reviewer group, and SLA.
