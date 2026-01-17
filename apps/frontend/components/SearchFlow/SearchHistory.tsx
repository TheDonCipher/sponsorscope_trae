"use client";

import { useState, useEffect } from 'react';
import { Clock, ExternalLink, Trash2, History } from 'lucide-react';

interface SearchHistoryItem {
  id: string;
  handle: string;
  platform: string;
  timestamp: Date;
  status: 'completed' | 'failed' | 'expired';
  confidence?: number;
}

interface SearchHistoryProps {
  isVisible: boolean;
  onClose: () => void;
  onSelectItem: (handle: string) => void;
}

export default function SearchHistory({ isVisible, onClose, onSelectItem }: SearchHistoryProps) {
  const [history, setHistory] = useState<SearchHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (isVisible) {
      // Simulate loading search history
      setTimeout(() => {
        const mockHistory: SearchHistoryItem[] = [
          {
            id: '1',
            handle: '@techcreator',
            platform: 'Instagram',
            timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
            status: 'completed',
            confidence: 87
          },
          {
            id: '2',
            handle: '@fashioninfluencer',
            platform: 'TikTok',
            timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
            status: 'completed',
            confidence: 92
          },
          {
            id: '3',
            handle: '@fitnesscoach',
            platform: 'YouTube',
            timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5), // 5 hours ago
            status: 'expired',
            confidence: 78
          }
        ];
        setHistory(mockHistory);
        setIsLoading(false);
      }, 1000);
    }
  }, [isVisible]);

  const getTimeAgo = (timestamp: Date) => {
    const now = new Date();
    const diffInMs = now.getTime() - timestamp.getTime();
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      return `${diffInDays}d ago`;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-emerald-600 dark:text-emerald-400';
      case 'failed':
        return 'text-red-600 dark:text-red-400';
      case 'expired':
        return 'text-slate-500 dark:text-slate-400';
      default:
        return 'text-slate-600 dark:text-slate-400';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
      case 'expired':
        return 'Expired';
      default:
        return 'Unknown';
    }
  };

  const clearHistory = () => {
    setHistory([]);
    // In a real app, this would call an API to clear the history
  };

  const removeItem = (id: string) => {
    setHistory(history.filter(item => item.id !== id));
    // In a real app, this would call an API to remove the item
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-slate-900 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-3">
            <History className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <div>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                Recent Observation Requests
              </h2>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Previously analyzed creator profiles
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <ExternalLink className="w-5 h-5 text-slate-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <History className="w-8 h-8 text-slate-400 mx-auto mb-3 animate-pulse" />
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Loading observation history...
                </p>
              </div>
            </div>
          ) : history.length === 0 ? (
            <div className="text-center py-12">
              <History className="w-12 h-12 text-slate-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
                No Recent Observations
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                Your recent creator observations will appear here
              </p>
              <button
                onClick={onClose}
                className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg font-medium transition-colors"
              >
                Start New Observation
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {history.map((item) => (
                <div
                  key={item.id}
                  className="p-4 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors group"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-medium text-slate-900 dark:text-slate-100">
                          {item.handle}
                        </h3>
                        <span className="text-xs px-2 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                          {item.platform}
                        </span>
                        <span className={`text-xs font-medium ${getStatusColor(item.status)}`}>
                          {getStatusLabel(item.status)}
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-slate-600 dark:text-slate-400">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          <span>{getTimeAgo(item.timestamp)}</span>
                        </div>
                        
                        {item.confidence && item.status === 'completed' && (
                          <div className="flex items-center gap-1">
                            <span>Confidence: {item.confidence}%</span>
                          </div>
                        )}
                        
                        {item.status === 'expired' && (
                          <span className="text-xs text-slate-500">
                            Data may be stale - consider re-analysis
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      {item.status !== 'expired' && (
                        <button
                          onClick={() => onSelectItem(item.handle)}
                          className="p-2 text-slate-500 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors"
                          title="View report"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </button>
                      )}
                      
                      <button
                        onClick={() => removeItem(item.id)}
                        className="p-2 text-slate-500 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                        title="Remove from history"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {history.length > 0 && (
          <div className="p-6 border-t border-slate-200 dark:border-slate-700">
            <div className="flex justify-between items-center">
              <p className="text-xs text-slate-500 dark:text-slate-400">
                History expires after 7 days for privacy protection
              </p>
              
              <button
                onClick={clearHistory}
                className="px-3 py-1 text-xs text-slate-600 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
              >
                Clear All History
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}