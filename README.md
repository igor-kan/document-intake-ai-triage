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
