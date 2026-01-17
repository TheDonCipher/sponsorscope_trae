# SponsorScope API

FastAPI application exposing public endpoints for report retrieval and correction requests.

## Endpoints
- GET /health — service health
- GET /api/report/{handle} — retrieve or generate a report for a handle
- POST /api/correction — submit a correction request tied to a report
- GET /api/evidence/{evidence_id} — placeholder for evidence retrieval

## Quick Start
```bash
cd services/api
pip install fastapi uvicorn pydantic
uvicorn main:app --reload --port 8000
```
Health: http://localhost:8000/health

## Implementation
- App entry: [main.py](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/services/api/main.py)
- Reports router: [reports.py](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/services/api/routes/reports.py)
- Assembler: [assembler.py](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/services/api/assembler.py)
- Models: [report.py](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/services/api/models/report.py)
- Epistemics: [epistemic.py](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/services/api/models/epistemic.py)

## Data Sources
- Scraper adapter (Instagram deterministic): [instagram.py](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/services/scraper/adapters/instagram.py)
- Heuristics:
  - Engagement: [engagement.py](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/services/analyzer/heuristics/engagement.py)
  - Authenticity: [authenticity.py](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/services/analyzer/heuristics/authenticity.py)

## Response Shape
`ReportResponse` includes:
- `data_completeness` and `epistemic_state`
- pillar scores: `true_engagement`, `audience_authenticity`, `brand_safety`, `niche_credibility`
- `evidence_vault`, `profile_metrics`, `warning_banners`

## Notes
- Kill switch in governance may return 503 during maintenance.
- Completeness values: full | partial_no_comments | unavailable | failed.
