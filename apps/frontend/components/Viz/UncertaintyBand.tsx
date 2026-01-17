import React from 'react';

interface UncertaintyBandProps {
  score: number; // 0-100
  confidence: number; // 0.0-1.0
  label?: string;
  showRangeLabels?: boolean;
}

export const UncertaintyBand: React.FC<UncertaintyBandProps> = ({ 
  score, 
  confidence, 
  label,
  showRangeLabels = true 
}) => {
  // Logic: Lower confidence = wider margin of error
  // Max margin is ±20% (at 0 confidence), Min is ±2% (at 1.0 confidence)
  const baseMargin = 20; 
  const margin = Math.max(2, (1 - confidence) * baseMargin);
  
  const low = Math.max(0, score - margin);
  const high = Math.min(100, score + margin);
  
  // Color logic based on confidence (not score)
  const rangeColorClass = confidence > 0.7 ? 'bg-blue-500/30' : 'bg-yellow-500/30';
  const medianColorClass = confidence > 0.7 ? 'bg-blue-400' : 'bg-yellow-400';

  return (
    <div className="w-full font-mono">
      {label && (
        <div className="flex justify-between items-end mb-1">
           <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold">{label}</span>
           <span className="text-xs text-white font-bold">
             {low.toFixed(0)}% - {high.toFixed(0)}%
           </span>
        </div>
      )}
      
      <div className="relative h-6 w-full bg-slate-800/50 rounded-md overflow-hidden" role="meter" aria-valuenow={score} aria-valuemin={low} aria-valuemax={high} aria-label={`${label || 'Metric'} estimated between ${low.toFixed(0)} and ${high.toFixed(0)} percent`}>
        {/* Background Grid Lines (10% increments) */}
        <div className="absolute inset-0 flex justify-between px-[1px]">
           {[...Array(11)].map((_, i) => (
             <div key={i} className={`h-full w-[1px] ${i === 0 || i === 10 ? 'bg-transparent' : 'bg-white/5'}`}></div>
           ))}
        </div>

        {/* The Uncertainty Band (Range) */}
        <div 
            className={`absolute top-1 bottom-1 rounded-sm backdrop-blur-sm ${rangeColorClass} border-l border-r border-white/10`}
            style={{ left: `${low}%`, width: `${high - low}%` }}
        >
            {/* Gradient Overlay for "Fuzziness" */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"></div>
        </div>

        {/* The Median Marker (Projected Value) */}
        <div 
            className={`absolute top-0 bottom-0 w-0.5 ${medianColorClass} shadow-[0_0_10px_rgba(96,165,250,0.8)]`}
            style={{ left: `${score}%` }}
        ></div>
      </div>

      {showRangeLabels && (
        <div className="flex justify-between text-[10px] text-slate-600 mt-1">
          <span>0</span>
          <span className="text-slate-500">EST. RANGE</span>
          <span>100</span>
        </div>
      )}
    </div>
  );
};
