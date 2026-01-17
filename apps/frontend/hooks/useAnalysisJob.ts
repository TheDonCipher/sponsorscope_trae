import { useState, useEffect, useCallback } from 'react';
import { Report } from '../types/schema';

export type AnalysisPhase = 'scraping' | 'analysis' | 'finalizing' | 'completed' | 'failed';

export interface AnalysisJob {
  jobId: string;
  phase: AnalysisPhase;
  progress?: number;
  error?: string;
}

export interface UseAnalysisJobReturn {
  job: AnalysisJob | null;
  report: Report | null;
  loading: boolean;
  error: string | null;
  startAnalysis: (handle: string) => Promise<void>;
}

const POLLING_INTERVALS = {
  initial: 2000, // 2 seconds
  max: 30000, // 30 seconds
  backoffMultiplier: 1.5,
};

export const useAnalysisJob = (): UseAnalysisJobReturn => {
  const [job, setJob] = useState<AnalysisJob | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pollJobStatus = useCallback(async (jobId: string): Promise<void> => {
    let currentInterval = POLLING_INTERVALS.initial;
    let attempts = 0;
    const maxAttempts = 120; // 2 minutes max

    const poll = async (): Promise<void> => {
      if (attempts >= maxAttempts) {
        setError('Analysis timeout: Job took too long to complete');
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`/api/status/${jobId}`);
        
        if (!response.ok) {
          throw new Error(`Status check failed: ${response.status}`);
        }

        const statusData = await response.json();
        
        setJob({
          jobId,
          phase: statusData.phase || 'analysis',
          progress: statusData.progress,
          error: statusData.error,
        });

        if (statusData.phase === 'completed') {
          // Fetch the final report
          const reportResponse = await fetch(`/api/report/${jobId}`);
          
          if (!reportResponse.ok) {
            throw new Error(`Failed to fetch report: ${reportResponse.status}`);
          }
          
          const reportData = await reportResponse.json();
          setReport(reportData);
          setLoading(false);
          return;
        }

        if (statusData.phase === 'failed') {
          setError(statusData.error || 'Analysis failed');
          setLoading(false);
          return;
        }

        // Continue polling with backoff
        attempts++;
        currentInterval = Math.min(
          currentInterval * POLLING_INTERVALS.backoffMultiplier,
          POLLING_INTERVALS.max
        );

        setTimeout(poll, currentInterval);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Polling failed');
        setLoading(false);
      }
    };

    poll();
  }, []);

  const startAnalysis = useCallback(async (handle: string): Promise<void> => {
    setLoading(true);
    setError(null);
    setJob(null);
    setReport(null);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ handle }),
      });

      if (!response.ok) {
        if (response.status === 503) {
          throw new Error('System Maintenance: Our servers are currently over capacity or under maintenance. Please try again later.');
        }
        if (response.status === 404) {
          throw new Error('Account not found: We could not locate this handle on the platform.');
        }
        throw new Error(`Failed to start analysis: ${response.status}`);
      }

      const data = await response.json();
      const jobId = data.jobId;

      if (!jobId) {
        throw new Error('Invalid response: No job ID received');
      }

      // Start polling immediately
      pollJobStatus(jobId);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start analysis');
      setLoading(false);
    }
  }, [pollJobStatus]);

  return {
    job,
    report,
    loading,
    error,
    startAnalysis,
  };
};