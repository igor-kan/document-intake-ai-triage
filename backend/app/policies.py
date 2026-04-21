from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyResult:
    route_queue: str
    reviewer_group: str
    sla_hours: int


class DocumentPolicy:
    document_type = "default"

    def apply(self, priority: str) -> PolicyResult:
        return PolicyResult(route_queue="general_intake", reviewer_group="general", sla_hours=48)


class ScannedFormPolicy(DocumentPolicy):
    document_type = "scanned_form"

    def apply(self, priority: str) -> PolicyResult:
        return PolicyResult(route_queue="vision_review", reviewer_group="ocr_team", sla_hours=8 if priority == "high" else 24)


class PdfFormPolicy(DocumentPolicy):
    document_type = "pdf_form"

    def apply(self, priority: str) -> PolicyResult:
        return PolicyResult(route_queue="document_review", reviewer_group="case_ops", sla_hours=12 if priority == "high" else 36)


class TabularPolicy(DocumentPolicy):
    document_type = "tabular_data"

    def apply(self, priority: str) -> PolicyResult:
        return PolicyResult(route_queue="data_ingest", reviewer_group="data_ops", sla_hours=6 if priority == "high" else 24)


class StructuredPayloadPolicy(DocumentPolicy):
    document_type = "structured_payload"

    def apply(self, priority: str) -> PolicyResult:
        return PolicyResult(route_queue="schema_validation", reviewer_group="integration_ops", sla_hours=6 if priority == "high" else 18)


POLICY_REGISTRY = {
    ScannedFormPolicy.document_type: ScannedFormPolicy(),
    PdfFormPolicy.document_type: PdfFormPolicy(),
    TabularPolicy.document_type: TabularPolicy(),
    StructuredPayloadPolicy.document_type: StructuredPayloadPolicy(),
}


def resolve_policy(document_type: str) -> DocumentPolicy:
    return POLICY_REGISTRY.get(document_type, DocumentPolicy())
