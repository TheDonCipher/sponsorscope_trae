import React, { useState } from 'react';

export interface EvidenceItem {
  id: string;
  type: 'post' | 'comment' | 'statistic' | 'network' | 'text';
  content: string; // Raw text or JSON representation
  timestamp: string;
  sourceUrl?: string;
  severity: 'low' | 'medium' | 'high';
  isVerified?: boolean;
}

interface EvidenceCardProps {
  item: EvidenceItem;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({ item }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Neutral color mapping for severity
  const severityColors = {
    low: 'border-slate-700 bg-slate-800/50',
    medium: 'border-yellow-900/30 bg-yellow-900/10',
    high: 'border-purple-900/30 bg-purple-900/10'
  };

  const iconMap: Record<string, string> = {
    comment: 'chat_bubble',
    post: 'article',
    statistic: 'bar_chart',
    network: 'hub',
    text: 'text_fields',
    timestamp: 'schedule'
  };

  const renderContent = () => {
    if (item.type === 'comment') {
      return (
        <div className="bg-slate-800 p-3 rounded-lg rounded-tl-none border border-slate-700 relative ml-2">
            <div className="absolute -left-2 top-0 w-2 h-2 bg-slate-800 [clip-path:polygon(100%_0,0_0,100%_100%)]"></div>
            <p className="text-sm text-slate-200 italic">"{item.content}"</p>
        </div>
      );
    }
    return (
        <div className="font-mono text-xs text-slate-300 bg-black/20 p-3 rounded mb-3 overflow-x-auto whitespace-pre-wrap">
            {item.content}
        </div>
    );
  };

  return (
    <div className={`border rounded-lg p-4 transition-all ${severityColors[item.severity]} hover:border-slate-500`}>
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-slate-400 text-sm">
            {iconMap[item.type] || 'description'}
          </span>
          <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
            {item.type} artifact
          </span>
        </div>
        <span className="text-[10px] font-mono text-slate-500">
          {new Date(item.timestamp).toLocaleDateString()} {new Date(item.timestamp).toLocaleTimeString()}
        </span>
      </div>

      {/* Raw Content (The Evidence) */}
      {renderContent()}

      {/* Footer / Actions */}
      <div className="flex justify-between items-center border-t border-white/5 pt-3">
        <div className="flex gap-3">
            {item.sourceUrl ? (
                <a 
                    href={item.sourceUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-[10px] font-bold text-blue-400 hover:text-blue-300 transition-colors"
                >
                    VIEW SOURCE <span className="material-symbols-outlined text-[10px]">open_in_new</span>
                </a>
            ) : (
                <span className="flex items-center gap-1 text-[10px] font-bold text-slate-600 cursor-not-allowed" title="Source deleted or private">
                    SOURCE UNAVAILABLE <span className="material-symbols-outlined text-[10px]">visibility_off</span>
                </span>
            )}
        </div>
        
        {/* Correction Loop */}
        <button className="text-[10px] text-slate-500 hover:text-slate-300 transition-colors">
            Flag as False Positive
        </button>
      </div>
    </div>
  );
};
