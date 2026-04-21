from __future__ import annotations

from contextlib import asynccontextmanager
from io import BytesIO

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from PIL import Image, ImageOps

from .job_queue import IntakeJobQueue
from .ocr import extract_text_with_confidence
from .policies import resolve_policy
from .runtime import detect_ml_frameworks
from .triage import infer_document_type, infer_priority


@asynccontextmanager
async def lifespan(_app: FastAPI):
    job_queue.start(process_batch_document)
    try:
        yield
    finally:
        job_queue.stop()


app = FastAPI(title="Document Intake and AI Triage", version="0.3.0", lifespan=lifespan)
job_queue = IntakeJobQueue()


class BatchDocument(BaseModel):
    filename: str
    content_type: str = "application/octet-stream"
    text_hint: str = ""


class BatchSubmitRequest(BaseModel):
    documents: list[BatchDocument] = Field(min_length=1, max_length=100)


class ReviewRequest(BaseModel):
    document_index: int = Field(ge=0)
    corrected_document_type: str = Field(min_length=2)
    corrected_priority: str = Field(min_length=2)
    notes: str = ""


class JobListResponse(BaseModel):
    items: list[dict]


def analyze_document(
    *,
    filename: str,
    content_type: str,
    payload: bytes | None = None,
    text_hint: str = "",
) -> dict:
    size_bytes = len(payload) if payload else len(text_hint.encode("utf-8"))
    document_type = infer_document_type(filename, content_type)
    priority = infer_priority(filename)

    thumbnail_size = None
    extracted_text = text_hint.strip()
    ocr_confidence = 0.45 if extracted_text else 0.0
    ocr_engine = "text_hint" if extracted_text else "none"

    if payload and content_type.startswith("image/"):
        image = Image.open(BytesIO(payload)).convert("RGB")
        normalized = ImageOps.autocontrast(image)
        normalized.thumbnail((256, 256))
        thumbnail_size = list(normalized.size)

        extracted_text, ocr_confidence, ocr_engine = extract_text_with_confidence(payload)

    classification_confidence_map = {
        "scanned_form": 0.88,
        "pdf_form": 0.86,
        "tabular_data": 0.91,
        "structured_payload": 0.93,
        "unknown": 0.35,
    }
    classification_confidence = classification_confidence_map.get(document_type, 0.35)
    overall_confidence = round((classification_confidence + ocr_confidence) / 2, 2)

    policy = resolve_policy(document_type)
    policy_result = policy.apply(priority)

    return {
        "filename": filename,
        "content_type": content_type,
        "size_bytes": size_bytes,
        "document_type": document_type,
        "priority": priority,
        "thumbnail_size": thumbnail_size,
        "extracted_text": extracted_text,
        "confidence": {
            "classification": classification_confidence,
            "ocr": ocr_confidence,
            "overall": overall_confidence,
        },
        "ocr_engine": ocr_engine,
        "policy": {
            "route_queue": policy_result.route_queue,
            "reviewer_group": policy_result.reviewer_group,
            "sla_hours": policy_result.sla_hours,
        },
    }


def process_batch_document(document: dict) -> dict:
    return analyze_document(
        filename=document["filename"],
        content_type=document.get("content_type", "application/octet-stream"),
        text_hint=document.get("text_hint", ""),
    )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "phase": "phase-2", "version": app.version}


@app.get("/api/runtime")
def runtime() -> dict:
    return detect_ml_frameworks()


@app.post("/api/intake/triage")
async def triage_document(file: UploadFile = File(...), text_hint: str = Form(default="")) -> dict:
    raw = await file.read()
    return analyze_document(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        payload=raw,
        text_hint=text_hint,
    )


@app.post("/api/intake/batch/submit")
def submit_batch(request: BatchSubmitRequest) -> dict:
    serialized = [item.model_dump() for item in request.documents]
    job_id = job_queue.submit(serialized)
    return {"job_id": job_id, "status": "queued", "count": len(serialized)}


@app.get("/api/intake/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    job = job_queue.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    return job


@app.get("/api/intake/jobs")
def list_jobs(status: str | None = None) -> JobListResponse:
    items = []
    for job in job_queue.list_jobs():
        if status and job["status"] != status:
            continue
        items.append(job)
    items.sort(key=lambda item: item["submitted_at"], reverse=True)
    return JobListResponse(items=items)


@app.get("/api/intake/queue/stats")
def queue_stats() -> dict:
    return job_queue.stats()


@app.post("/api/intake/jobs/{job_id}/review")
def review_job(job_id: str, review: ReviewRequest) -> dict:
    updated = job_queue.add_review(job_id, review.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="job_not_found")

    return {
        "job_id": updated["job_id"],
        "reviews": updated["reviews"],
        "result": updated["results"][review.document_index] if updated["results"] else None,
    }
