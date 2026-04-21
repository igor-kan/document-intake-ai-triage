from io import BytesIO

from fastapi import FastAPI, File, UploadFile
from PIL import Image, ImageOps

from .runtime import detect_ml_frameworks
from .triage import infer_document_type, infer_priority

app = FastAPI(title="Document Intake and AI Triage")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/runtime")
def runtime() -> dict:
    return detect_ml_frameworks()


@app.post("/api/intake/triage")
async def triage_document(file: UploadFile = File(...)) -> dict:
    raw = await file.read()
    size_bytes = len(raw)
    document_type = infer_document_type(file.filename, file.content_type or "")
    priority = infer_priority(file.filename)

    thumbnail_size = None
    if file.content_type and file.content_type.startswith("image/"):
        image = Image.open(BytesIO(raw)).convert("RGB")
        normalized = ImageOps.autocontrast(image)
        normalized.thumbnail((256, 256))
        thumbnail_size = list(normalized.size)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": size_bytes,
        "document_type": document_type,
        "priority": priority,
        "thumbnail_size": thumbnail_size,
    }
