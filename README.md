# Document Intake + AI Triage

Uploads documents/images, performs normalization and lightweight triage, and returns structured routing hints for downstream processing.

## Stack

- FastAPI backend (Python)
- React frontend (Vite)
- Pillow for image preprocessing
- TensorFlow/PyTorch runtime checks for optional ML model loading

## Run Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8020
```

## Run Frontend

```bash
cd web
npm install
npm run dev
```

## API

- `GET /api/health`
- `GET /api/runtime`
- `POST /api/intake/triage` (multipart file upload)

<!-- REPO_ANALYSIS_OVERVIEW_START -->
## Repository Analysis Snapshot

Generated: 2026-04-21

- Primary stack: Unknown
- Key paths: `backend`, `docs`, `.github/workflows`, `README.md`
- Files scanned (capped): 26
- Test signal: Test-named files detected
- CI workflows present: Yes
- GitHub slug: igor-kan/document-intake-ai-triage
- GitHub last push: 2026-04-21T20:50:16Z

### Quick Commands

Setup:
- `Review repository README for setup steps`

Run:
- `Review repository README for run/start command`

Quality:
- `Review CI/workflow commands in .github/workflows`

### Companion Docs

- `AGENTS.md`
- `TASKS.md`
- `PLANNING.md`
- `RESEARCH.md`
- `PROJECT_BRIEF.md`

### Web Research References

- Origin remote: `https://github.com/igor-kan/document-intake-ai-triage.git`
- GitHub homepage: Not set
- `N/A`
<!-- REPO_ANALYSIS_OVERVIEW_END -->
