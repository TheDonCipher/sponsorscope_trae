import React from 'react';
import { ScoreExplanation } from '../ScoreExplanation/ScoreExplanation';
import { useReport } from '../../hooks/useReport';

interface ReportViewProps {
  handle: string;
}

export const ReportView: React.FC<ReportViewProps> = ({ handle }) => {
  const { report, loading, error } = useReport(handle);

  if (loading) return <div className="p-8 text-center text-gray-500">Generating Analysis...</div>;
  if (error) return <div className="p-8 text-center text-red-600">Error: {error}</div>;
  if (!report) return null;

  // Partial Data Banner (Non-dismissible)
  const isPartial = report.data_completeness !== 'full';

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      {/* 1. Header & Meta-Signal */}
      <div className="border-b pb-4">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{report.handle}</h1>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-500">
             Platform: <span className="capitalize">{report.platform}</span>
          </span>
          {/* Epistemic State Badge */}
          <span className={`px-2 py-1 text-xs font-bold rounded uppercase 
            ${report.epistemic_state.status === 'ROBUST' ? 'bg-green-100 text-green-800' : 
              report.epistemic_state.status === 'PARTIAL' ? 'bg-yellow-100 text-yellow-800' : 
              'bg-red-100 text-red-800'}`}>
            Data Reliability: {report.epistemic_state.status}
          </span>
        </div>
        {/* Epistemic Reason */}
        <p className="mt-2 text-sm text-gray-600 italic">
          "{report.epistemic_state.reason}"
        </p>
      </div>

      {/* 2. Mandatory Warning Banners */}
      {isPartial && (
        <div className="bg-orange-50 border-l-4 border-orange-500 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              {/* Icon placeholder */}
              ⚠️
            </div>
            <div className="ml-3">
              <p className="text-sm text-orange-700">
                <strong>Incomplete Data Warning:</strong> This report is based on partial data. 
                Do not use for comparative ranking.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 3. Pillars (Visualized via ScoreExplanation) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section>
          <h2 className="text-xl font-semibold mb-4 text-gray-800">True Engagement Signal</h2>
          <ScoreExplanation 
            score={report.true_engagement.signal_strength}
            uncertainty={[
              report.true_engagement.signal_strength - 5, // Mock calc for UI demo
              report.true_engagement.signal_strength + 5 
            ]}
            confidence={report.true_engagement.confidence}
            factors={report.true_engagement.flags}
            limitations={report.known_limitations}
          />
        </section>

        <section>
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Audience Authenticity Signal</h2>
          <ScoreExplanation 
            score={report.audience_authenticity.signal_strength}
            uncertainty={[
               report.audience_authenticity.signal_strength - (1 - report.audience_authenticity.confidence) * 20,
               report.audience_authenticity.signal_strength + (1 - report.audience_authenticity.confidence) * 20
            ]}
            confidence={report.audience_authenticity.confidence}
            factors={report.audience_authenticity.flags}
            limitations={report.known_limitations}
          />
        </section>
      </div>

      {/* 4. Evidence Vault Link */}
      <div className="mt-8 pt-6 border-t">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Evidence Vault</h3>
        <div className="bg-gray-50 rounded p-4 text-sm text-gray-600">
           {report.evidence_vault.length} evidence items available. 
           <button className="ml-2 text-blue-600 hover:underline">View Raw Data</button>
        </div>
      </div>
      
      {/* 5. Footer / Legal */}
      <div className="text-center text-xs text-gray-400 pt-8 pb-4">
        <p>SponsorScope Signal v2.3 | Generated: {new Date(report.generated_at).toLocaleDateString()}</p>
        <p className="mt-1">Probabilistic research estimate. Not financial advice.</p>
      </div>
    </div>
  );
};
