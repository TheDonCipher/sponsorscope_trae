import { useState, useEffect } from 'react';
import { Report } from '../types/schema';

export const useReport = (handle: string) => {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/report/${handle}`);
        if (!response.ok) {
           if (response.status === 503) throw new Error('System Maintenance');
           if (response.status === 404) throw new Error('Report not found');
           throw new Error('Failed to fetch report');
        }
        const data = await response.json();
        setReport(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    if (handle) {
      fetchReport();
    }
  }, [handle]);

  return { report, loading, error };
};
