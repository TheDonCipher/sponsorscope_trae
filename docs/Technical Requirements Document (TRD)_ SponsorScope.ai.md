# Technical Requirements Document (TRD): SponsorScope.ai

**Version:** 1.1  
**Status:** Final - Incorporating Structural Improvements  
**Cloud Provider:** Google Cloud Platform (GCP) - Native Services Only

---

## 1. Architecture Principles
*   **Hybrid Analysis:** Reduce LLM dependency by using rule-based heuristics for baseline scores, with Gemini providing nuance.
*   **Graceful Degradation:** Design for partial data availability (e.g., comments blocked, images missing).
*   **Epistemic Integrity:** Implement confidence intervals and versioned methodology in the data schema.
*   **Google-Native Stack:** Maximize managed services (Cloud Run, Firestore, Cloud Storage, Vertex AI).

## 2. Functional Requirements
### 2.1. Data Ingestion & Resilience
*   **FR-INGEST-01:** Accept `@handle` or URL; sanitize inputs.
*   **FR-INGEST-02:** **Degradation Logic:** If a platform blocks specific data (e.g., comments), the scraper must flag the `data_completeness` status (e.g., `full`, `partial_no_comments`, `archival`).
*   **FR-INGEST-03:** Store raw JSON in GCS with 30-day lifecycle.
*   **FR-INGEST-04:** Implement proxy rotation and stealth Playwright configurations.

### 2.2. Hybrid AI Analysis
*   **FR-AI-01:** **Deterministic Heuristics:** Compute "Bot Probability Floor" using statistical entropy of comment timestamps and text repetition *before* LLM processing.
*   **FR-AI-02:** **LLM Refinement:** Use `gemini-1.5-flash` to interpret nuance (e.g., code-switching, Setswana slang) and refine the heuristic scores.
*   **FR-AI-03:** **Confidence Scoring:** Generate a `confidence_score` (0-1.0) based on data volume and AI consistency.
*   **FR-AI-04:** **Brand Safety:** Perform OCR and text analysis; if images are blocked, fallback to text-only safety grading with a visible warning.

### 2.3. Report Serving & Governance
*   **FR-REP-01:** Check Firestore for cached reports (< 7 days).
*   **FR-REP-02:** **Correction Log:** Maintain a Firestore collection for public correction requests and their status.
*   **FR-REP-03:** **Methodology Versioning:** Every report must store the `methodology_version` used to ensure auditability.

## 3. Non-Functional Requirements
*   **NFR-PERF-01:** Cached report response time < 1.5s.
*   **NFR-REL-01:** **Scraping Resilience:** System must return a "Partial Report" rather than a 500 error if 50% of data is retrieved.
*   **NFR-SEC-01:** Sanitize all inputs; implement rate limiting via Cloud Armor.
*   **NFR-COST-01:** Target average cost per fresh report < $0.10.

## 4. Technology Stack
| Component | Technology |
| :--- | :--- |
| **Frontend** | Next.js 14 + Tailwind CSS |
| **Backend API** | Python FastAPI (Cloud Run) |
| **Scraper** | Python Playwright (Cloud Run Jobs) |
| **Analysis Engine** | Python (Pandas/NumPy for heuristics) + Vertex AI (Gemini) |
| **Task Queue** | Cloud Tasks |
| **Database** | Firestore (Native Mode) |
| **Storage** | Cloud Storage (GCS) |

## 5. Data Modeling (Firestore)
### `reports` Collection
```json
{
  "handle": "@creator_bw",
  "methodology_version": "v1.1",
  "data_completeness": "partial_no_comments",
  "confidence_interval": [72, 78],
  "pillars": {
    "true_engagement": {"score": 75, "is_heuristic": true},
    "audience_authenticity": {"score": 68, "llm_refined": true},
    "brand_safety": {"grade": "B", "fallback_mode": "text_only"}
  },
  "last_analyzed": "Timestamp",
  "expires_at": "Timestamp"
}
```

## 6. Deployment & Governance
*   **CI/CD:** Cloud Build with automated smoke tests for scraping success.
*   **Regional Calibration:** Use a dedicated `calibration_set` of Botswana influencers to validate model updates before deployment.
