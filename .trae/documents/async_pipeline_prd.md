## 1. Product Overview

Convert the current synchronous report generation system into an asynchronous pipeline to improve API response times and handle long-running analysis tasks efficiently. This enables users to submit analysis requests and receive immediate acknowledgment while processing occurs in the background.

The async pipeline solves the problem of long API response times (currently blocking for entire analysis) and provides better user experience through progress tracking and job management.

## 2. Core Features

### 2.1 User Roles

No role distinction required for this backend API enhancement.

### 2.2 Feature Module

Our async pipeline requirements consist of the following main API endpoints:

1. **Analysis submission**: Accept handle and platform, return job ID immediately
2. **Status tracking**: Provide real-time progress updates with phase and percentage
3. **Report retrieval**: Fetch completed analysis results

### 2.3 Page Details

| Page Name                 | Module Name         | Feature description                                                                                                                               |
| ------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| POST /api/analyze         | Analysis submission | Accept handle and optional platform parameter, validate input, create unique job ID, return 202 Accepted response with job\_id within 200ms       |
| GET /api/status/{job\_id} | Status tracking     | Return current job status including ScrapeStatus, processing phase ("Scraping"/"Analysis"/"Finalizing"), and completion percentage when available |
| GET /api/report/{job\_id} | Report retrieval    | Return complete ReportResponse with all analysis results, scores, and evidence when job is completed                                              |

## 3. Core Process

The async pipeline follows a three-step process:

1. **Job Submission**: User submits handle and platform via POST /api/analyze, receives immediate 202 response with job\_id
2. **Background Processing**: System processes scraping → analysis → assembly in background while user can poll status
3. **Result Retrieval**: User fetches completed report via GET /api/report/{job\_id}

```mermaid
graph TD
    A[User submits analysis request] --> B[POST /api/analyze]
    B --> C{Validation & Deduplication}
    C -->|New job| D[Create job ID & enqueue]
    C -->|Duplicate| E[Return existing job ID]
    D --> F[Return 202 + job_id]
    E --> F
    F --> G[Background worker starts]
    G --> H[Scraping phase]
    H --> I[Analysis phase]
    I --> J[Finalizing phase]
    J --> K[Job completed]
    L[User polls status] --> M[GET /api/status/{job_id}]
    M --> N{Job status?}
    N -->|Processing| O[Return status + progress]
    N -->|Completed| P[Ready for retrieval]
    P --> Q[GET /api/report/{job_id}]
    Q --> R[Return ReportResponse]
```

## 4. User Interface Design

### 4.1 Design Style

* **Response format**: JSON API responses with consistent structure

* **Status codes**: Standard HTTP status codes (202, 200, 404, 500)

* **Error handling**: Structured error responses with descriptive messages

* **Job identification**: UUID-based job IDs for uniqueness

* **Progress indication**: Percentage-based progress when available

### 4.2 Page Design Overview

| Page Name                 | Module Name         | UI Elements                                                                         |
| ------------------------- | ------------------- | ----------------------------------------------------------------------------------- |
| POST /api/analyze         | Analysis submission | JSON request body with handle/platform, JSON response with job\_id, 202 status code |
| GET /api/status/{job\_id} | Status tracking     | JSON response with status, phase, percent fields, appropriate HTTP status codes     |
| GET /api/report/{job\_id} | Report retrieval    | Complete ReportResponse JSON with all analysis data, evidence vault, and metrics    |

### 4.3 Responsiveness

* **API response time**: POST /api/analyze must respond within 200ms

* **Status polling**: Support frequent polling (1-5 second intervals)

* **Timeout handling**: Jobs should complete within reasonable time limits

### 4.4 Performance Requirements

* **Job creation**: ≤200ms response time for POST /api/analyze

* **Status queries**: ≤100ms response time for GET /api/status/{job\_id}

* **Report retrieval**: ≤500ms response time for completed reports

* **Concurrent jobs**: Support multiple simultaneous background processes

* **Memory management**: TTL-based cleanup for completed jobs

