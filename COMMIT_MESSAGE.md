feat: implement async job-based analysis with clear progress states

- Add useAnalysisJob hook for job-based async analysis workflow
  - POST /api/analyze to start analysis jobs
  - Poll /api/status/{job_id} with exponential backoff (2s→30s)
  - Fetch final report from /api/report/{job_id} when completed
  - Handle timeouts, errors, and edge cases with 2-minute max limit

- Create AnalysisProgress component for clear analysis phases
  - Show distinct phases: Scraping, Analysis, Finalizing
  - Display descriptive text explaining current operation
  - Progress bar with phase indicators (no fake progress)
  - Time estimate warning banner
  - Responsive design with visual hierarchy

- Update ReportView to use job-based endpoints
  - Replace useReport with useAnalysisJob hook
  - Show AnalysisProgress during job processing
  - Maintain existing warning banner functionality
  - Preserve all report visualization features

- Key improvements:
  - Clear "Analysis in Progress" state with explanatory text
  - No spinner without explanatory text
  - Real progress based on job status (no fake progress)
  - Warning banners for partial data via getWarningBanner
  - Exponential backoff polling reduces server load
  - Comprehensive error handling for network/API issues

- Testing:
  - Add test page at /test for verification
  - Build passes TypeScript checks successfully
  - Maintains existing UI/UX design patterns

BREAKING CHANGE: ReportView now requires job-based API endpoints
(/api/analyze, /api/status/{id}, /api/report/{id}) instead of
legacy /api/report/{handle} polling approach.