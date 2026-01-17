import React from 'react';
import { AnalysisPhase } from '../../hooks/useAnalysisJob';

interface AnalysisProgressProps {
  phase: AnalysisPhase;
  progress?: number;
  handle: string;
}

const phaseDescriptions = {
  scraping: {
    title: 'Scraping Profile Data',
    description: 'Collecting public posts, engagement metrics, and profile information',
    icon: 'download',
    color: 'blue',
  },
  analysis: {
    title: 'Analyzing Signals',
    description: 'Processing engagement patterns, audience authenticity, and brand safety metrics',
    icon: 'analytics',
    color: 'purple',
  },
  finalizing: {
    title: 'Finalizing Report',
    description: 'Compiling findings and generating confidence scores',
    icon: 'fact_check',
    color: 'green',
  },
};

const phaseOrder: AnalysisPhase[] = ['scraping', 'analysis', 'finalizing'];

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ phase, progress, handle }) => {
  const currentPhaseIndex = phaseOrder.indexOf(phase);
  const currentPhaseInfo = phaseDescriptions[phase] || phaseDescriptions.analysis;

  return (
    <div className="flex items-center justify-center min-h-screen bg-background-dark text-white">
      <div className="flex flex-col items-center gap-8 max-w-md w-full px-6">
        {/* Progress Header */}
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold">Analysis in Progress</h2>
          <p className="text-white/60 text-sm">Processing @{handle}</p>
        </div>

        {/* Phase Progress Bar */}
        <div className="w-full space-y-4">
          <div className="flex justify-between text-xs text-white/40">
            {phaseOrder.map((p, index) => (
              <span 
                key={p} 
                className={`${
                  index <= currentPhaseIndex ? 'text-white' : ''
                } transition-colors`}
              >
                {phaseDescriptions[p].title}
              </span>
            ))}
          </div>
          
          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
            <div 
              className={`h-full bg-${currentPhaseInfo.color}-500 transition-all duration-1000 ease-out`}
              style={{ 
                width: `${progress ? Math.min(progress, 95) : currentPhaseIndex === 0 ? 15 : currentPhaseIndex === 1 ? 50 : 85}%` 
              }}
            />
          </div>
        </div>

        {/* Current Phase Info */}
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 w-full space-y-4">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 bg-${currentPhaseInfo.color}-500/20 border border-${currentPhaseInfo.color}-500/30 rounded-lg flex items-center justify-center`}>
              <span className="material-symbols-outlined text-${currentPhaseInfo.color}-400">
                {currentPhaseInfo.icon}
              </span>
            </div>
            <div>
              <h3 className="font-bold">{currentPhaseInfo.title}</h3>
              <p className="text-xs text-white/60">{currentPhaseInfo.description}</p>
            </div>
          </div>

          {progress && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-white/60">Progress:</span>
              <span className="font-mono text-${currentPhaseInfo.color}-400">{progress}%</span>
            </div>
          )}
        </div>

        {/* Time Estimate */}
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 w-full">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-yellow-500 text-sm">schedule</span>
            <span className="text-sm text-yellow-500/80">
              Analysis may take up to 2 minutes depending on account size
            </span>
          </div>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center gap-2 text-sm text-white/40">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span>Processing...</span>
        </div>
      </div>
    </div>
  );
};