import React from 'react';

interface ConfidenceMeterProps {
  level: number; // 0.0 - 1.0
  compact?: boolean;
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({ level, compact = false }) => {
  // Determine state
  const isHigh = level >= 0.8;
  const isMed = level >= 0.5 && level < 0.8;
  
  const colorClass = isHigh ? 'text-blue-400' : isMed ? 'text-yellow-400' : 'text-purple-400';
  const label = isHigh ? 'ROBUST' : isMed ? 'PARTIAL' : 'FRAGILE';
  const bars = 5;
  const filledBars = Math.ceil(level * bars);

  if (compact) {
     return (
        <div className="flex items-center gap-1.5" title={`Data Confidence: ${(level * 100).toFixed(0)}%`}>
            <div className="flex items-end gap-[1px] h-3">
                {[...Array(bars)].map((_, i) => (
                    <div 
                        key={i} 
                        className={`w-1 rounded-sm ${i < filledBars ? (isHigh ? 'bg-blue-400' : isMed ? 'bg-yellow-400' : 'bg-purple-400') : 'bg-slate-700'}`}
                        style={{ height: `${(i + 1) * 20}%` }}
                    ></div>
                ))}
            </div>
        </div>
     );
  }

  return (
    <div className="flex items-center gap-2 font-mono text-xs">
      <span className="text-slate-500 uppercase tracking-wider text-[10px] font-bold">Confidence</span>
      <div className="flex items-center gap-2 bg-slate-800/50 px-2 py-1 rounded border border-white/5">
        <div className="flex items-end gap-[1px] h-3">
            {[...Array(bars)].map((_, i) => (
                <div 
                    key={i} 
                    className={`w-1 rounded-sm ${i < filledBars ? (isHigh ? 'bg-blue-400' : isMed ? 'bg-yellow-400' : 'bg-purple-400') : 'bg-slate-700'}`}
                    style={{ height: `${(i + 1) * 20}%` }}
                ></div>
            ))}
        </div>
        <span className={`${colorClass} font-bold`}>{label}</span>
        <span className="text-slate-600">|</span>
        <span className="text-slate-400">{(level * 100).toFixed(0)}%</span>
      </div>
    </div>
  );
};
