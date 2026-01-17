"use client";

import { AlertCircle, Info, RotateCcw, ExternalLink } from 'lucide-react';

interface ObservationErrorProps {
  errorType: 'insufficient_data' | 'private_account' | 'platform_limitation' | 'network_error';
  onRetry?: () => void;
  onCancel?: () => void;
}

export default function ObservationError({ errorType, onRetry, onCancel }: ObservationErrorProps) {
  const getErrorDetails = () => {
    switch (errorType) {
      case 'insufficient_data':
        return {
          title: "Insufficient Public Data",
          description: "We could not observe enough public activity to proceed with the analysis",
          details: [
            "The profile may be too new or have limited public content",
            "Privacy settings may restrict access to engagement data",
            "Recent activity may not meet our minimum observation threshold"
          ],
          suggestions: [
            "Try again with a different public creator profile",
            "Ensure the account has been active for at least 30 days",
            "Check that the profile has public posts and engagement"
          ],
          color: "amber"
        };
      
      case 'private_account':
        return {
          title: "Private Account Detected",
          description: "This profile is not accessible for public observation",
          details: [
            "The account privacy settings prevent public data collection",
            "Only publicly visible activity can be observed",
            "This is a privacy protection, not a system limitation"
          ],
          suggestions: [
            "Use a public creator profile for analysis",
            "Respect privacy settings and user preferences",
            "Consider profiles that maintain public visibility"
          ],
          color: "blue"
        };
      
      case 'platform_limitation':
        return {
          title: "Platform Access Limitation",
          description: "Platform restrictions prevent complete observation",
          details: [
            "Rate limiting or API restrictions may apply",
            "Platform policies may change access availability",
            "Some content types may be temporarily unavailable"
          ],
          suggestions: [
            "Wait a few minutes and try again",
            "Try analyzing a different platform profile",
            "Contact support if the issue persists"
          ],
          color: "purple"
        };
      
      case 'network_error':
        return {
          title: "Network Connection Issue",
          description: "A connection problem prevented data collection",
          details: [
            "Temporary network connectivity issues",
            "Server response timeout during observation",
            "Intermittent service availability"
          ],
          suggestions: [
            "Check your internet connection",
            "Try refreshing the page and submitting again",
            "Contact support if problems continue"
          ],
          color: "red"
        };
      
      default:
        return {
          title: "Observation Error",
          description: "An unexpected issue occurred during the observation process",
          details: ["Unknown error type encountered"],
          suggestions: ["Please try again or contact support"],
          color: "gray"
        };
    }
  };

  const errorDetails = getErrorDetails();
  
  const getColorClasses = (color: string) => {
    const colorMap = {
      amber: {
        bg: "bg-amber-50 dark:bg-amber-900/20",
        border: "border-amber-200 dark:border-amber-800",
        text: "text-amber-800 dark:text-amber-200",
        subtext: "text-amber-700 dark:text-amber-300",
        icon: "text-amber-600 dark:text-amber-400"
      },
      blue: {
        bg: "bg-blue-50 dark:bg-blue-900/20",
        border: "border-blue-200 dark:border-blue-800",
        text: "text-blue-800 dark:text-blue-200",
        subtext: "text-blue-700 dark:text-blue-300",
        icon: "text-blue-600 dark:text-blue-400"
      },
      purple: {
        bg: "bg-purple-50 dark:bg-purple-900/20",
        border: "border-purple-200 dark:border-purple-800",
        text: "text-purple-800 dark:text-purple-200",
        subtext: "text-purple-700 dark:text-purple-300",
        icon: "text-purple-600 dark:text-purple-400"
      },
      red: {
        bg: "bg-red-50 dark:bg-red-900/20",
        border: "border-red-200 dark:border-red-800",
        text: "text-red-800 dark:text-red-200",
        subtext: "text-red-700 dark:text-red-300",
        icon: "text-red-600 dark:text-red-400"
      },
      gray: {
        bg: "bg-slate-50 dark:bg-slate-800",
        border: "border-slate-200 dark:border-slate-700",
        text: "text-slate-800 dark:text-slate-200",
        subtext: "text-slate-700 dark:text-slate-300",
        icon: "text-slate-600 dark:text-slate-400"
      }
    };
    
    return colorMap[color as keyof typeof colorMap] || colorMap.gray;
  };

  const colors = getColorClasses(errorDetails.color);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className={`bg-white dark:bg-slate-900 rounded-lg shadow-xl max-w-2xl w-full mx-4 p-6 border ${colors.border}`}>
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <AlertCircle className={`w-6 h-6 ${colors.icon}`} />
          <div>
            <h2 className={`text-xl font-semibold ${colors.text}`}>
              {errorDetails.title}
            </h2>
            <p className={`text-sm ${colors.subtext} mt-1`}>
              {errorDetails.description}
            </p>
          </div>
        </div>

        {/* Details */}
        <div className="space-y-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Info className={`w-4 h-4 ${colors.icon}`} />
              <h3 className={`text-sm font-medium ${colors.text}`}>
                What we attempted:
              </h3>
            </div>
            <ul className={`text-sm ${colors.subtext} space-y-1 ml-6`}>
              {errorDetails.details.map((detail, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-xs mt-1">•</span>
                  <span>{detail}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-2">
              <ExternalLink className={`w-4 h-4 ${colors.icon}`} />
              <h3 className={`text-sm font-medium ${colors.text}`}>
                What you can do:
              </h3>
            </div>
            <ul className={`text-sm ${colors.subtext} space-y-1 ml-6`}>
              {errorDetails.suggestions.map((suggestion, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-xs mt-1">•</span>
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-between items-center pt-4 border-t border-slate-200 dark:border-slate-700">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
          >
            Cancel Request
          </button>
          
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <RotateCcw className="w-4 h-4" />
              Try Again
            </button>
          )}
        </div>

        {/* Educational Note */}
        <div className={`mt-4 p-3 rounded-lg ${colors.bg} border ${colors.border}`}>
          <p className={`text-xs ${colors.subtext}`}>
            <strong>System Transparency:</strong> This error message is designed to help you understand 
            observational limitations. These are normal constraints of working with public data, not system failures.
          </p>
        </div>
      </div>
    </div>
  );
}