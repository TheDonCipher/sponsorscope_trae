import React, { useState } from 'react';

interface ScoreExplanationProps {
  score: number;
  uncertainty: [number, number]; // [low, high]
  confidence: number;
  factors: string[]; // e.g., ["timing_concentration", "graph_reuse"]
  limitations: string[];
}

export const ScoreExplanation: React.FC<ScoreExplanationProps> = ({
  score,
  uncertainty,
  confidence,
  factors,
  limitations
}) => {
  const [expanded, setExpanded] = useState(false);
  
  // Calculate band width for visualization
  const range = uncertainty[1] - uncertainty[0];
  const center = score;
  
  // Determine color based on confidence (NOT score)
  const confidenceColor = confidence > 0.8 ? 'bg-green-100 text-green-800' :
                         confidence > 0.5 ? 'bg-yellow-100 text-yellow-800' :
                         'bg-red-100 text-red-800';

  return (
    <div className="border rounded-lg p-4 shadow-sm bg-white">
      {/* Header: Confidence First */}
      <div className="flex items-center justify-between mb-2">
        <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${confidenceColor}`}>
          {confidence > 0.8 ? 'High Confidence' : confidence > 0.5 ? 'Moderate Confidence' : 'Low Confidence'}
        </span>
        <span className="text-gray-500 text-xs">Methodology v2.3</span>
      </div>

      {/* Score & Uncertainty Visualization */}
      <div className="flex items-baseline space-x-2 mb-4">
        <span className="text-4xl font-bold text-gray-900">{score.toFixed(0)}</span>
        <span className="text-lg text-gray-500 font-medium">
          ± {((uncertainty[1] - score)).toFixed(0)}
        </span>
      </div>
      
      {/* Range Bar */}
      <div className="relative h-2 bg-gray-200 rounded-full mb-4 overflow-hidden">
        <div 
          className="absolute h-full bg-blue-500 opacity-20"
          style={{ 
            left: `${uncertainty[0]}%`, 
            width: `${range}%` 
          }}
        />
        <div 
          className="absolute h-full w-1 bg-blue-600"
          style={{ left: `${score}%` }}
        />
      </div>

      {/* Expandable Context */}
      <button 
        onClick={() => setExpanded(!expanded)}
        className="text-sm text-blue-600 hover:text-blue-800 font-medium focus:outline-none"
      >
        {expanded ? 'Hide Details' : 'Why this signal?'}
      </button>

      {expanded && (
        <div className="mt-4 space-y-3 text-sm text-gray-700">
          <div>
            <h4 className="font-bold text-gray-900">Observed Patterns</h4>
            {factors.length > 0 ? (
              <ul className="list-disc list-inside mt-1">
                {factors.map((f, i) => (
                  <li key={i} className="capitalize">{f.replace(/_/g, ' ')}</li>
                ))}
              </ul>
            ) : (
              <p className="italic text-gray-500">No atypical patterns detected.</p>
            )}
          </div>
          
          <div>
            <h4 className="font-bold text-gray-900">Known Limitations</h4>
             <ul className="list-disc list-inside mt-1 text-gray-600">
                {limitations.map((l, i) => (
                  <li key={i}>{l}</li>
                ))}
              </ul>
          </div>
          
          <div className="pt-2 border-t text-xs text-gray-500">
            <p>
              <strong>Disclaimer:</strong> SponsorScope provides probabilistic research estimates, 
              not factual determinations or judgments.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
