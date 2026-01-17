"use client";
import { useState } from 'react';
import { useAnalysisJob } from '../../hooks/useAnalysisJob';

export default function TestPage() {
  const [handle, setHandle] = useState('');
  const { job, report, loading, error, startAnalysis } = useAnalysisJob();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (handle.trim()) {
      await startAnalysis(handle.trim());
    }
  };

  return (
    <div className="min-h-screen bg-background-dark text-white p-8">
      <div className="max-w-2xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold">Test Async Analysis</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Enter Handle to Analyze:
            </label>
            <input
              type="text"
              value={handle}
              onChange={(e) => setHandle(e.target.value)}
              placeholder="e.g., example_user"
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:border-blue-500"
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            disabled={loading || !handle.trim()}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg font-medium"
          >
            {loading ? 'Analyzing...' : 'Start Analysis'}
          </button>
        </form>

        {error && (
          <div className="bg-red-500/20 border border-red-500/40 rounded-lg p-4">
            <h3 className="font-bold text-red-400">Error:</h3>
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {job && (
          <div className="bg-white/10 border border-white/20 rounded-lg p-4">
            <h3 className="font-bold mb-2">Current Job Status:</h3>
            <p>Phase: <span className="text-blue-400">{job.phase}</span></p>
            {job.progress && <p>Progress: <span className="text-green-400">{job.progress}%</span></p>}
            {job.error && <p className="text-red-400">Error: {job.error}</p>}
          </div>
        )}

        {report && (
          <div className="bg-green-500/20 border border-green-500/40 rounded-lg p-4">
            <h3 className="font-bold text-green-400 mb-2">Analysis Complete!</h3>
            <p>Handle: @{report.handle}</p>
            <p>Platform: {report.platform}</p>
            <p>Confidence: {(report.true_engagement.confidence * 100).toFixed(0)}%</p>
            <p>Data Completeness: {report.data_completeness}</p>
          </div>
        )}
      </div>
    </div>
  );
}