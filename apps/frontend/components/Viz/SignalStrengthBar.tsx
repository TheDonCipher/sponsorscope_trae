import React from 'react';

interface SignalStrengthBarProps {
  value: number; // 0-100
  threshold?: number;
  label: string;
}

export const SignalStrengthBar: React.FC<SignalStrengthBarProps> = ({ value, threshold, label }) => {
  return (
    <div className="w-full">
      <div className="flex justify-between text-[10px] uppercase font-bold text-slate-400 mb-1">
        <span>{label}</span>
        <span className="text-white font-mono">{value.toFixed(1)}</span>
      </div>
      
      <div className="relative h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
        {/* Fill */}
        <div 
            className="absolute top-0 bottom-0 left-0 bg-blue-500 rounded-full transition-all duration-500"
            style={{ width: `${value}%` }}
        ></div>
        
        {/* Threshold Marker */}
        {threshold && (
            <div 
                className="absolute top-0 bottom-0 w-0.5 bg-white/50 z-10"
                style={{ left: `${threshold}%` }}
                title={`Benchmark: ${threshold}`}
            ></div>
        )}
      </div>
    </div>
  );
};
