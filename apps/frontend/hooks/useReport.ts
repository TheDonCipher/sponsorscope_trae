import { useState, useEffect } from 'react';
import { Report } from '../types/schema';

export const useReport = (handle: string) => {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    let timeoutId: NodeJS.Timeout;

    const fetchReport = async () => {
      // Only set loading to true initially if we don't have data
      // or if we want to show a full screen loader. 
      // For this UX, we want the "terminal" loader to show until 200 OK.
      setLoading(true);
      setError(null);
      
      const poll = async () => {
        try {
          const response = await fetch(`/api/report/${handle}`);
          
          if (!isMounted) return;

          if (response.status === 200) {
            const data = await response.json();
            setReport(data);
            setLoading(false);
            return;
          }
          
          if (response.status === 202) {
             // 202 Accepted: The request has been accepted for processing, 
             // but the processing has not been completed.
             // Poll again after 2 seconds.
             timeoutId = setTimeout(poll, 2000);
             return;
          }

          if (response.status === 503) throw new Error('System Maintenance: Our servers are currently over capacity or under maintenance. Please try again later.');
          if (response.status === 410) throw new Error('Data Gone: This report has been permanently removed or the account is no longer accessible.');
          if (response.status === 404) throw new Error('Report not found: We could not locate this handle on the platform.');
          
          throw new Error(`Failed to fetch report (Status: ${response.status})`);
        } catch (err) {
          if (isMounted) {
            setError(err instanceof Error ? err.message : 'Unknown error');
            setLoading(false);
          }
        }
      };

      poll();
    };

    if (handle) {
      fetchReport();
    }

    return () => {
      isMounted = false;
      if (timeoutId) clearTimeout(timeoutId);
    };
  }, [handle]);

  return { report, loading, error };
};
