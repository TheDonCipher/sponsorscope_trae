"use client";

import { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Navbar } from '../../components/Navbar';
import { Footer } from '../../components/Footer';

function CorrectionForm() {
  const searchParams = useSearchParams();
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    handle: '',
    metric: 'signal_consistency',
    reason: 'context_missing',
    description: ''
  });

  useEffect(() => {
    const handle = searchParams.get('handle');
    if (handle) {
      setFormData(prev => ({ ...prev, handle }));
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
        // Map frontend reason to backend IssueType
        // Backend types: data_incomplete, comments_disabled, private_account, platform_error, context_missing
        const issueTypeMap: Record<string, string> = {
            'missing_context': 'context_missing',
            'missing_data': 'data_incomplete',
            'timestamp_error': 'platform_error',
            'other': 'platform_error',
            'context_missing': 'context_missing' // Default
        };

        const response = await fetch('/api/correction', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                handle: formData.handle,
                issue_type: issueTypeMap[formData.reason] || 'context_missing',
                explanation: `[${formData.metric}] ${formData.description}`,
                report_id: "unknown" 
            })
        });
        
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Submission failed');
        }
        
        const result = await response.json();
        if (result.status === 'denied') {
            throw new Error(`Request denied: ${result.denial_reason}`);
        }
        
        setSubmitted(true);
    } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
        setIsSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-background-light dark:bg-background-dark text-[#101816] dark:text-white font-display flex flex-col">
        <Navbar />
        <main className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-surface-light dark:bg-surface-dark p-8 rounded-xl border border-green-500/30 text-center">
            <div className="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="material-symbols-outlined text-3xl text-green-500">check_circle</span>
            </div>
            <h2 className="text-2xl font-bold mb-4">Request Received</h2>
            <p className="text-slate-600 dark:text-slate-400 mb-8 leading-relaxed">
              We have flagged <strong>@{formData.handle}</strong> for a priority re-scan. 
              Our analysts will review the provided context. If the new parameters alter the baseline, the report will be updated automatically.
            </p>
            <Link href="/" className="inline-block px-6 py-3 bg-primary text-[#101816] font-bold rounded-lg hover:bg-emerald-400 transition-colors">
              Return to Dashboard
            </Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark text-[#101816] dark:text-white font-display flex flex-col">
      <Navbar />
      <main className="flex-1 max-w-2xl mx-auto w-full px-6 py-12">
        <div className="mb-8">
            <Link href="/" className="flex items-center gap-2 text-sm text-slate-500 hover:text-primary mb-4">
                <span className="material-symbols-outlined text-[16px]">arrow_back</span>
                Back to Dashboard
            </Link>
            <h1 className="text-3xl font-bold mb-2">Report a Data Discrepancy</h1>
            <p className="text-slate-600 dark:text-slate-400">
                Help us improve accuracy. If you believe a metric is statistically flawed or missing context, let us know.
                <br/> <span className="text-sm italic opacity-70">Note: We cannot manually edit scores, but we can recalibrate the model parameters.</span>
            </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8 bg-surface-light dark:bg-surface-dark p-8 rounded-xl border border-border-light dark:border-border-dark">
            
            {/* Error Banner */}
            {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-500 text-sm font-bold flex items-center gap-2">
                    <span className="material-symbols-outlined">error</span>
                    {error}
                </div>
            )}

            {/* Handle Input */}
            <div>
                <label className="block text-sm font-bold mb-2 uppercase tracking-wider text-slate-500">Account Handle</label>
                <div className="relative">
                    <span className="absolute left-4 top-3.5 text-slate-400">@</span>
                    <input 
                        required
                        type="text" 
                        value={formData.handle}
                        onChange={(e) => setFormData({...formData, handle: e.target.value})}
                        className="w-full pl-8 pr-4 py-3 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:ring-2 focus:ring-primary focus:outline-none"
                        placeholder="username"
                    />
                </div>
            </div>

            {/* Metric Selector */}
            <div>
                <label className="block text-sm font-bold mb-2 uppercase tracking-wider text-slate-500">Affected Metric</label>
                <select 
                    value={formData.metric}
                    onChange={(e) => setFormData({...formData, metric: e.target.value})}
                    className="w-full px-4 py-3 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:ring-2 focus:ring-primary focus:outline-none appearance-none"
                >
                    <option value="signal_consistency">Signal Consistency (Engagement)</option>
                    <option value="audience_patterns">Audience Patterns</option>
                    <option value="brand_safety">Brand Safety</option>
                    <option value="other">Other / Metadata</option>
                </select>
            </div>

            {/* Reason Selector */}
            <div>
                <label className="block text-sm font-bold mb-2 uppercase tracking-wider text-slate-500">Nature of Discrepancy</label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {['missing_context', 'timestamp_error', 'missing_data', 'other'].map((r) => (
                        <div 
                            key={r}
                            onClick={() => setFormData({...formData, reason: r})}
                            className={`p-4 rounded-lg border cursor-pointer transition-all ${formData.reason === r ? 'border-primary bg-primary/10' : 'border-border-light dark:border-border-dark hover:border-slate-400'}`}
                        >
                            <span className="block font-bold capitalize mb-1">{r.replace('_', ' ')}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Context Textarea */}
            <div>
                <label className="block text-sm font-bold mb-2 uppercase tracking-wider text-slate-500">Additional Context</label>
                <textarea 
                    required
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="w-full px-4 py-3 rounded-lg bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark focus:ring-2 focus:ring-primary focus:outline-none min-h-[120px]"
                    placeholder="E.g., 'The spike on Jan 12th was due to a viral repost by @bigaccount...'"
                ></textarea>
                <p className="text-xs text-slate-500 mt-2 text-right">{formData.description.length}/500 characters</p>
            </div>

            {/* Submit Button */}
            <div className="pt-4 border-t border-border-light dark:border-border-dark">
                <button 
                    type="submit" 
                    disabled={isSubmitting}
                    className="w-full bg-primary text-[#101816] font-bold py-4 rounded-lg hover:bg-emerald-400 transition-colors shadow-lg shadow-primary/20 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isSubmitting ? (
                        <>
                            <span className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin"></span>
                            Submitting...
                        </>
                    ) : (
                        <>
                            <span className="material-symbols-outlined">send</span>
                            Submit Correction Request
                        </>
                    )}
                </button>
                <p className="text-xs text-center text-slate-500 mt-4">
                    By submitting, you certify that you have a legitimate interest in the accuracy of this data.
                </p>
            </div>
        </form>
      </main>
      <Footer />
    </div>
  );
}

export default function CorrectionPage() {
    return (
        <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
            <CorrectionForm />
        </Suspense>
    );
}
