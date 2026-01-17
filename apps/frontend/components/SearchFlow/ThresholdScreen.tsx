"use client";

import { useState } from 'react';
import { CheckCircle, AlertTriangle, BarChart3, Clock, Shield } from 'lucide-react';

interface ThresholdScreenProps {
  isVisible: boolean;
  onViewReport: () => void;
  dataCompleteness: {
    posts: number;
    engagement: number;
    comments: number;
    total: number;
  };
  confidence: {
    level: 'high' | 'medium' | 'low';
    percentage: number;
    factors: string[];
  };
  warnings?: string[];
}

export default function ThresholdScreen({ 
  isVisible, 
  onViewReport, 
  dataCompleteness, 
  confidence, 
  warnings = [] 
}: ThresholdScreenProps) {
  const [isAcknowledged, setIsAcknowledged] = useState(false);

  if (!isVisible) return null;

  const getConfidenceColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800';
      case 'medium':
        return 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800';
      case 'low':
        return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      default:
        return 'text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700';
    }
  };

  const getConfidenceLabel = (level: string) => {
    switch (level) {
      case 'high':
        return 'High Confidence';
      case 'medium':
        return 'Medium Confidence';
      case 'low':
        return 'Low Confidence';
      default:
        return 'Unknown Confidence';
    }
  };

  const completenessPercentage = Math.round((dataCompleteness.total / 12) * 100);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-slate-900 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-6 border-b border-slate-200 dark:border-slate-700">
          <div className="text-center">
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-2">
              Observation Complete
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Review the observational parameters before proceeding to the report
            </p>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Data Completeness */}
          <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <BarChart3 className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                Data Completeness
              </h3>
            </div>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-600 dark:text-slate-400">Posts observed</span>
                <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                  {dataCompleteness.posts}/12
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-600 dark:text-slate-400">Engagement data</span>
                <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                  {dataCompleteness.engagement}/12
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-slate-600 dark:text-slate-400">Comments accessible</span>
                <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                  {dataCompleteness.comments}/12
                </span>
              </div>
              
              <div className="pt-3 border-t border-slate-200 dark:border-slate-700">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Overall completeness</span>
                  <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                    {completenessPercentage}%
                  </span>
                </div>
                <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${completenessPercentage}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Confidence Assessment */}
          <div className={`p-4 rounded-lg border ${getConfidenceColor(confidence.level)}`}>
            <div className="flex items-center gap-3 mb-4">
              <Shield className="w-5 h-5" />
              <h3 className="text-lg font-semibold">
                {getConfidenceLabel(confidence.level)}
              </h3>
              <span className="text-sm font-medium ml-auto">
                {confidence.percentage}%
              </span>
            </div>
            
            <div className="space-y-2">
              <p className="text-sm opacity-90">
                Confidence level based on:
              </p>
              <ul className="text-sm space-y-1">
                {confidence.factors.map((factor, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-xs mt-1">•</span>
                    <span>{factor}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Warnings */}
          {warnings && warnings.length > 0 && (
            <div className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
              <div className="flex items-center gap-3 mb-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                <h3 className="text-lg font-semibold text-amber-800 dark:text-amber-200">
                  Observational Limitations
                </h3>
              </div>
              <ul className="text-sm text-amber-700 dark:text-amber-300 space-y-2">
                {warnings.map((warning, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-xs mt-1">•</span>
                    <span>{warning}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Acknowledgment */}
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={isAcknowledged}
                onChange={(e) => setIsAcknowledged(e.target.checked)}
                className="mt-1 w-4 h-4 text-blue-500 border-blue-300 dark:border-blue-600 rounded focus:ring-blue-500"
              />
              <div>
                <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
                  I understand this is an observational report based on publicly available data
                </p>
                <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                  Results should be interpreted as probabilistic indicators, not definitive conclusions
                </p>
              </div>
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-slate-200 dark:border-slate-700">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
              <Clock className="w-4 h-4" />
              <span>Report generated: {new Date().toLocaleTimeString()}</span>
            </div>
            <button
              onClick={onViewReport}
              disabled={!isAcknowledged}
              className="px-6 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-300 dark:disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              View Observational Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}