import { useState, useCallback } from 'react';

export interface PlatformResistanceError {
  type: 'platform_resistance' | 'rate_limit' | 'abuse_detection' | 'maintenance' | 'token_limit';
  message: string;
  details?: {
    halt_reason?: string;
    halt_timestamp?: string;
    scraper_guidance?: string;
    contact_info?: string;
    client_ip?: string;
  };
  user_facing_message?: string;
  data_integrity_verdict?: string;
}

interface UsePlatformResistanceReturn {
  error: PlatformResistanceError | null;
  isResisted: boolean;
  handleResistanceError: (error: any) => void;
  clearResistanceError: () => void;
  retryRequest: () => void;
}

export const usePlatformResistance = (): UsePlatformResistanceReturn => {
  const [error, setError] = useState<PlatformResistanceError | null>(null);

  const handleResistanceError = useCallback((error: any) => {
    console.error('Platform resistance error:', error);

    // Check if this is a platform resistance error
    if (error?.response?.data?.type === 'platform_resistance') {
      setError(error.response.data);
    } else if (error?.response?.status === 429) {
      // Rate limit error
      setError({
        type: 'rate_limit',
        message: error.response.data?.message || 'Rate limit exceeded',
        user_facing_message: 'Too many requests. Please try again later.',
        details: error.response.data?.remaining
      });
    } else if (error?.response?.status === 403 && error?.response?.data?.type === 'abuse_detection') {
      // Abuse detection error
      setError({
        type: 'abuse_detection',
        message: error.response.data?.message || 'Request blocked',
        user_facing_message: 'Request blocked due to suspicious activity.',
        details: error.response.data?.details
      });
    } else if (error?.response?.status === 503) {
      // Maintenance or token limit
      const errorType = error.response.data?.type;
      setError({
        type: errorType === 'token_limit' ? 'token_limit' : 'maintenance',
        message: error.response.data?.message || 'Service temporarily unavailable',
        user_facing_message: error.response.data?.message || 'Service temporarily unavailable',
        details: error.response.data?.details
      });
    } else {
      // Generic error that might be platform resistance
      const errorData = error?.response?.data;
      if (errorData?.type === 'platform_resistance' || errorData?.data_integrity_verdict) {
        setError(errorData);
      }
    }
  }, []);

  const clearResistanceError = useCallback(() => {
    setError(null);
  }, []);

  const retryRequest = useCallback(() => {
    // Clear error and let the parent component handle retry logic
    clearResistanceError();
    
    // Dispatch a custom event that components can listen to
    window.dispatchEvent(new CustomEvent('platform-resistance-retry'));
  }, [clearResistanceError]);

  return {
    error,
    isResisted: !!error,
    handleResistanceError,
    clearResistanceError,
    retryRequest
  };
};

export default usePlatformResistance;