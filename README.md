# SponsorScope.ai - System Scaffold (Phase 1)

**SponsorScope.ai** is a public, open-access influencer intelligence platform designed as a transparency-first public utility.

## 1. Repository Structure (Monorepo)

```text
.
├── apps
│   ├── frontend          # Next.js 14 Frontend (UI & Reporting)
│   └── api               # FastAPI Gateway (Governance & Orchestration)
├── services
│   ├── scraper           # Python Playwright Worker (Cloud Run Job)
│   └── analyzer          # Python Analysis Engine (Heuristics + Vertex AI)
├── shared
│   ├── schemas           # Shared Pydantic Models (Versioned Domain Core)
│   └── contracts         # Abstract Base Classes for Scoring Logic
├── docs                  # PRD, TRD, SDD
└── README.md             # This file
```

## 2. System Boundaries & Data Flow

The system is designed for **graceful degradation** and **auditability**.

```mermaid
graph TD
    User((User)) -->|1. Search @handle| API[API Gateway]
    API -->|2. Check Cache| Firestore[(Firestore)]
    
    subgraph "Ingestion Layer"
        API -->|3. Dispatch Job| TaskQueue[Cloud Tasks]
        TaskQueue -->|4. Trigger| Scraper[Scraper Worker]
        Scraper -->|5. Raw HTML/JSON| GCS[(Cloud Storage)]
        Scraper -.->|Fail/Partial| API
    end
    
    subgraph "Analysis Layer"
        Scraper -->|6. Trigger Analysis| AnalysisQueue[Analysis Queue]
        AnalysisQueue -->|7. Process| Analyzer[Analysis Engine]
        Analyzer -->|8. Load Raw| GCS
        Analyzer -->|9. Heuristics| HeuristicEngine[Heuristics (NumPy)]
        HeuristicEngine -->|10. Baseline Score| LLMRefiner[Vertex AI Refiner]
        LLMRefiner -->|11. Final Report| Firestore
    end
    
    Firestore -->|12. Return Report| API
    API -->|13. Render| Frontend
```

### Critical Flow Control
- **Failures Allowed**: Individual scraping steps (e.g., comments blocked). System must set `DataCompleteness` flag.
- **Partial Data**: Accepted. Heuristics adapt (e.g., if no comments, `True Engagement` score uses only Likes/Views with higher uncertainty).
- **System Halt**: Only if profile does not exist or API is unreachable.

## 3. Core Domain Models (`shared/schemas`)

- **InfluencerProfile**: Normalized identity.
- **Report**: The primary output, versioned and immutable.
- **RawPost / RawComment**: Intermediate raw data.
- **DataCompleteness**: Enum controlling degradation (`FULL`, `PARTIAL_NO_COMMENTS`, etc.).

## 4. Scoring Contracts (`shared/contracts`)

- **HeuristicScorer**: Deterministic, rule-based (Python/NumPy).
- **LLMRefiner**: Nuance-based, strictly bounded (Vertex AI).
- **Guarantees**: All scorers must declare `required_inputs`, `output_range`, and `is_deterministic`.

## 5. Phase 2: Implementation TODOs

### Scraper Worker
- [ ] Implement Playwright adapters for Instagram/TikTok.
- [ ] Implement exponential backoff and proxy rotation.
- [ ] Implement GCS upload logic (JSON serialization).
- [ ] Handle "Login Wall" and "Captcha" as graceful failures.

### Analysis Engine
- [ ] Implement `TrueEngagementScorer` (Heuristic).
- [ ] Implement `AudienceAuthenticityScorer` (Heuristic: Entropy/Velocity).
- [ ] Implement `BrandSafetyScorer` (Hybrid: Keyword matching + Gemini).
- [ ] Implement `GeminiRefiner` with Vertex AI SDK.
- [ ] Implement "Confidence Interval" calculation logic.

### API Gateway
- [ ] Implement `GET /reports/{handle}` with cache logic.
- [ ] Implement `POST /analyze` task dispatch.
- [ ] Implement `GET /methodology` endpoint.

### Frontend
- [ ] Build "Influencer Search" component.
- [ ] Build "Report Dashboard" with Confidence Interval visualization.
- [ ] Implement "Evidence Modal" (linking to raw data).
- [ ] Implement "Correction Log" UI.

### Shared
- [ ] Write unit tests for Heuristic Scorers (ensure determinism).
- [ ] Create `MethodologyMetadata` version `v1.0` configuration.
