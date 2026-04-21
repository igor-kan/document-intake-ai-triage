from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from queue import Empty, Queue
from threading import Event, Lock, Thread
from typing import Any, Callable
from uuid import uuid4


class IntakeJobQueue:
    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}
        self._queue: Queue[str] = Queue()
        self._lock = Lock()
        self._stop = Event()
        self._worker: Thread | None = None
        self._processor: Callable[[dict[str, Any]], dict[str, Any]] | None = None

    def start(self, processor: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        self._processor = processor
        if self._worker and self._worker.is_alive():
            return

        self._stop.clear()
        self._worker = Thread(target=self._run, daemon=True)
        self._worker.start()

    def stop(self) -> None:
        self._stop.set()
        if self._worker:
            self._worker.join(timeout=1.0)

    def submit(self, documents: list[dict[str, Any]]) -> str:
        job_id = str(uuid4())
        with self._lock:
            self._jobs[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "submitted_at": datetime.now(UTC).isoformat(),
                "documents": documents,
                "results": [],
                "reviews": [],
            }

        self._queue.put(job_id)
        return job_id

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            item = self._jobs.get(job_id)
            return deepcopy(item) if item else None

    def add_review(self, job_id: str, review: dict[str, Any]) -> dict[str, Any] | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None

            job["reviews"].append(review)
            index = review["document_index"]
            if 0 <= index < len(job["results"]):
                target = job["results"][index]
                target["document_type"] = review["corrected_document_type"]
                target["priority"] = review["corrected_priority"]
                target["human_review"] = {
                    "notes": review.get("notes", ""),
                    "applied": True,
                }

            return deepcopy(job)

    def list_jobs(self) -> list[dict[str, Any]]:
        with self._lock:
            return [deepcopy(item) for item in self._jobs.values()]

    def stats(self) -> dict[str, int]:
        with self._lock:
            items = list(self._jobs.values())
            return {
                "total_jobs": len(items),
                "queued_jobs": sum(1 for item in items if item["status"] == "queued"),
                "processing_jobs": sum(1 for item in items if item["status"] == "processing"),
                "completed_jobs": sum(1 for item in items if item["status"] == "completed"),
            }

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                job_id = self._queue.get(timeout=0.2)
            except Empty:
                continue

            try:
                self._process(job_id)
            finally:
                self._queue.task_done()

    def _process(self, job_id: str) -> None:
        if self._processor is None:
            return

        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job["status"] = "processing"
            documents = list(job["documents"])

        results: list[dict[str, Any]] = []
        for doc in documents:
            try:
                result = self._processor(doc)
            except Exception as exc:
                result = {
                    "filename": doc.get("filename", "unknown"),
                    "status": "failed",
                    "error": str(exc),
                }
            results.append(result)

        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job["results"] = results
            job["completed_at"] = datetime.now(UTC).isoformat()
            job["status"] = "completed"
