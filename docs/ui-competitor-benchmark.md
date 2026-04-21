# UI Competitor Benchmark

## Competitors Reviewed

- Rossum Intelligent Document Processing: https://rossum.ai/intelligent-document-processing/
- UiPath Document Understanding: https://docs.uipath.com/document-understanding/automation-cloud/latest/user-guide/about-document-understanding
- ABBYY Vantage Overview: https://docs.abbyy.com/home

## Key Patterns Observed

- IDP tools emphasize queue visibility, SLA awareness, and human validation handoff.
- Confidence signals are surfaced per document/field for review prioritization.
- Batch workflows and monitoring are first-class UX elements.

## Implemented Adaptations

- Added queue stats and job listing endpoints.
- Added batch submission + polling UX in frontend.
- Added confidence block and policy routing metadata in triage response.
- Added explicit human-review correction endpoint and flow.
