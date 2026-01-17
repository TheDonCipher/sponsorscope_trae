# SponsorScope.ai

SponsorScope.ai is a public, open-access influencer intelligence platform focused on transparency, auditability, and graceful degradation when data is limited.

**Status**: MVP implementation live in the monorepo. Frontend renders reports for any handle using deterministic mock scraping and heuristic analysis. API exposes report and correction endpoints. Shared domain and contracts formalize core types.

**Key Links**
- Frontend hook: [useReport.ts](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/apps/frontend/hooks/useReport.ts)
- Frontend types: [schema.ts](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/apps/frontend/types/schema.ts)
- API app entry: [main.py](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/services/api/main.py)
- API routes: [reports.py](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/services/api/routes/reports.py)
- Report assembly: [assembler.py](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/services/api/assembler.py)
- Domain enums: [domain.py](file:///c:/Users/Japan/OneDrive/Documents/GitHub/sponsorscope_trae/shared/schemas/domain.py)

## Monorepo Structure

```text
.
├── apps
│   └── frontend          # Next.js 14 app (UI & reporting)
├── services
│   ├── api               # FastAPI app exposing report & correction endpoints
│   ├── scraper           # Deterministic Instagram scraper (mocked, interface-complete)
│   └── analyzer          # Heuristic scoring + LLM stubs
├── shared
│   ├── schemas           # Shared domain models and enums
│   └── contracts         # Scoring abstractions
└── docs                  # PRD/TRD/SDD + UX design docs
```

## Features
- Deterministic scraper simulating Instagram profiles, posts, and comments for any handle.
- Heuristic analysis producing pillar scores:
  - True Engagement
  - Audience Authenticity
  - Brand Safety (placeholder with sensible defaults)
  - Niche Credibility (V2 placeholder)
- Epistemic state and DataCompleteness signaling for graceful degradation.
- Evidence vault and metrics for traceability and context.
- Frontend routes including report dashboard, methodology, correction flow, and more.

## Architecture Overview

```mermaid
graph TD
    User((User)) -->|/report/@handle| Frontend
    Frontend -->|fetch /api/report/{handle}| API
    API --> Scraper
    Scraper --> Analyzer
    Analyzer --> Assembler
    Assembler --> API
    API --> Frontend
```

### Flow Guarantees
- Failures allowed per step; global completeness tracked via `DataCompleteness`.
- Partial data accepted; confidence and epistemic status reflect uncertainty.
- Only halts for unavailable profiles or system maintenance.

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+

### Install
```bash
# From repo root
npm install --prefix apps/frontend
python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt  # if present; otherwise install fastapi+uvicorn
pip install fastapi uvicorn pydantic
```

### Run Frontend
```bash
cd apps/frontend
npm run dev
```
Open http://localhost:3000 and visit /report/somehandle.

### Run API
```bash
cd services/api
uvicorn main:app --reload --port 8000
```
The API mounts routes under /api. Health: http://localhost:8000/health

## API Reference

Base: http://localhost:8000

- GET /api/report/{handle}
  - Returns a report with pillar scores, evidence links, and metadata.
  - Completeness values: full | partial_no_comments | failed | unavailable
  - Example:
    ```bash
    curl http://localhost:8000/api/report/exampleuser
    ```

- POST /api/correction
  - Submit a correction request with issue type and optional explanation.
  - Example JSON:
    ```json
    {
      "handle": "exampleuser",
      "issue_type": "DATA_ERROR",
      "explanation": "Comment counts appear inflated",
      "report_id": "unknown"
    }
    ```

## Frontend Routes
- /report/[handle] — Report overview and visualization
- /methodology — Public methodology and audit notes
- /correction — Submit corrections and feedback
- /docs — System documentation
- /help — Help and FAQs
- /pricing — Placeholder pricing page
- /settings — User preferences (MVP shell)

## Domain & Contracts
- DataCompleteness enum and Platform declarations in shared domain.
- Heuristic results combined in assembler to produce ReportResponse.
- Evidence generation includes deterministic history series for UI.

## Contributing

We welcome issues and pull requests that improve transparency and rigor.

- Fork the repo and create a feature branch.
- Add tests for analysis heuristics where feasible.
- Keep docs updated; changes to API or frontend routes must be reflected in README files.
- Follow a conventional commit style where possible (feat, fix, docs, chore).
- Open a PR with a clear summary and links to affected files.

See CONTRIBUTING.md for detailed guidelines.

## License
Apache-2.0 (or project-specific; update as needed)
