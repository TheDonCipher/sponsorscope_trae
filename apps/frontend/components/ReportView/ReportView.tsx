import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAnalysisJob } from '../../hooks/useAnalysisJob';
import { AnalysisProgress } from '../AnalysisProgress/AnalysisProgress';
import { ConfidenceMeter } from '../Viz/ConfidenceMeter';
import { UncertaintyBand } from '../Viz/UncertaintyBand';
import { SignalStrengthBar } from '../Viz/SignalStrengthBar';
import { EvidenceCard, EvidenceItem } from '../Viz/EvidenceCard';
import { WarningBanner, WarningType } from '../Viz/WarningBanner';
import { Report } from '../../types/schema';

interface ReportViewProps {
  handle: string;
}

export const ReportView: React.FC<ReportViewProps> = ({ handle }) => {
  const { job, report, loading, error, startAnalysis } = useAnalysisJob();

  // Start analysis when component mounts
  useEffect(() => {
    if (handle) {
      startAnalysis(handle);
    }
  }, [handle, startAnalysis]);

  if (loading && job) {
    return <AnalysisProgress phase={job.phase} progress={job.progress} handle={handle} />;
  }

  if (loading) {
    // Fallback for initial loading state
    return (
      <div className="flex items-center justify-center min-h-screen bg-background-dark text-white">
        <div className="flex flex-col items-center gap-6">
          <div className="relative">
              <div className="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-8 h-8 bg-primary/10 rounded-full animate-pulse"></div>
              </div>
          </div>
          <div className="text-center">
              <p className="animate-pulse font-mono text-primary font-bold tracking-widest text-sm mb-2">INITIALIZING ANALYSIS...</p>
              <p className="text-xs text-white/40 font-mono">ANALYSIS SUBJECT: @{handle}</p>
              <p className="text-xs text-yellow-500/80 mt-4 font-bold uppercase tracking-wider">Analysis may take up to 2 minutes</p>
          </div>
        </div>
      </div>
    );
  }
  
  if (error) return (
    <div className="flex items-center justify-center min-h-screen bg-background-dark text-white">
      <div className="bg-red-500/10 border border-red-500/20 p-8 rounded-xl max-w-md text-center backdrop-blur-md">
        <span className="material-symbols-outlined text-4xl text-red-500 mb-4">warning</span>
        <h3 className="text-xl font-bold mb-2 text-red-400">Scan Failed</h3>
        <p className="text-white/60 mb-6 font-mono text-sm">{error}</p>
        <button onClick={() => window.location.reload()} className="px-6 py-2 bg-red-500 hover:bg-red-600 rounded-lg font-bold transition-colors text-white shadow-lg shadow-red-500/20">
          Retry Sequence
        </button>
      </div>
    </div>
  );

  if (!report) return null;

  // Chart Helper
  const generateChartPath = (data: number[]) => {
      if (!data || data.length === 0) return "M0,300 L1000,300";
      const width = 1000;
      const height = 300;
      const padding = 50;
      
      const points = data.map((val, i) => {
          const x = (i / (data.length - 1)) * width;
          const y = height - ((val / 100) * (height - padding));
          return `${x},${y}`;
      });
      
      return `M ${points.join(' ')}`;
  };

  const chartPath = generateChartPath(report.true_engagement.history);
  const chartFill = `${chartPath} L 1000,300 L 0,300 Z`;

  // Ghost Watermark Style
  const watermarkStyle = {
    backgroundImage: `repeating-linear-gradient(
      45deg,
      transparent,
      transparent 100px,
      rgba(255, 255, 255, 0.03) 100px,
      rgba(255, 255, 255, 0.03) 200px
    )`
  };

  // Determine Warning Banner
  const getWarningBanner = (report: Report) => {
      if (report.data_completeness === 'partial_no_comments') {
          return <WarningBanner type="blocked" />;
      }
      if (report.data_completeness === 'unavailable' || report.data_completeness === 'archival') {
           return <WarningBanner type="system" message="This report is based on archival data. Live signals may vary." />;
      }
       if (report.data_completeness === 'text_only') {
           return <WarningBanner type="sparse" message="Visual analysis unavailable. Report limited to text signals." />;
      }
      return null;
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background-dark text-white font-grotesk selection:bg-neon-lime selection:text-black relative">
        {/* Persistent Watermark Overlay */}
        <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden" style={watermarkStyle}>
            <div className="w-full h-full flex flex-wrap content-start opacity-5 transform -rotate-12 scale-150">
                {Array(50).fill(0).map((_, i) => (
                    <div key={i} className="m-12 font-black text-4xl text-white whitespace-nowrap">
                        SPONSORSCOPE • @{handle} • {new Date().toLocaleDateString()} • PROBABILISTIC ESTIMATE
                    </div>
                ))}
            </div>
        </div>
      {/* Sidebar Navigation */}
      <aside className="w-72 flex-shrink-0 flex flex-col border-r border-white/10 bg-background-dark/50 backdrop-blur-xl hidden lg:flex">
        <div className="p-6 flex flex-col h-full">
          {/* Logo Section */}
          <div className="flex items-center gap-3 mb-10 cursor-pointer" onClick={() => window.location.href='/'}>
            <div className="bg-neon-lime p-1.5 rounded-lg shadow-glow">
              <span className="material-symbols-outlined text-black font-bold">query_stats</span>
            </div>
            <div>
              <h1 className="text-white text-lg font-bold leading-none">SponsorScope.ai</h1>
              <p className="text-neon-lime/60 text-[10px] uppercase tracking-widest font-bold mt-1">Intelligence Suite</p>
            </div>
          </div>
          {/* Nav Links */}
          <nav className="flex-1 space-y-2">
            <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-neon-lime/10 text-neon-lime border border-neon-lime/20 shadow-sm">
              <span className="material-symbols-outlined text-[20px] fill-1">dashboard</span>
              <p className="text-sm font-bold">Dashboard</p>
            </div>
            <Link href="/methodology" className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors cursor-pointer group">
              <span className="material-symbols-outlined text-[20px] text-white/60 group-hover:text-white">menu_book</span>
              <p className="text-sm font-medium text-white/70 group-hover:text-white">Methodology Appendix</p>
            </Link>
            <Link href="/context" className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors cursor-pointer group">
              <span className="material-symbols-outlined text-[20px] text-white/60 group-hover:text-white">info</span>
              <p className="text-sm font-medium text-white/70 group-hover:text-white">Research Context</p>
            </Link>
            <Link href="/correction" className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors cursor-pointer group">
              <span className="material-symbols-outlined text-[20px] text-white/60 group-hover:text-white">flag</span>
              <p className="text-sm font-medium text-white/70 group-hover:text-white">Correction Request</p>
            </Link>
          </nav>
          {/* Sidebar Footer */}
          <div className="pt-6 border-t border-white/10 space-y-4">
            <div className="bg-neon-lime/5 rounded-lg p-4 border border-neon-lime/10">
              <p className="text-[10px] uppercase tracking-wider text-neon-lime font-bold mb-2">Research Context</p>
              <p className="text-[11px] leading-relaxed text-white/60">Currently analyzing North American lifestyle vertical benchmarks for Q3 2024 compliance.</p>
            </div>
            <button className="w-full bg-neon-lime text-black py-3 rounded-lg text-sm font-black flex items-center justify-center gap-2 hover:bg-neon-lime/90 transition-transform active:scale-[0.98] shadow-glow">
              <span className="material-symbols-outlined text-[18px]">picture_as_pdf</span>
              EXPORT PDF REPORT
            </button>
            <Link href="/help" className="flex items-center gap-3 px-3 py-2 text-white/50 hover:text-white cursor-pointer">
              <span className="material-symbols-outlined text-[20px]">help</span>
              <p className="text-xs font-medium">Help Center</p>
            </Link>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto scrollbar-hide">
        {/* Epistemic State Banner */}
        <div className="bg-slate-800/50 border-b border-white/5 px-8 py-3 flex items-center justify-between">
            <div className="flex items-center gap-6">
                <ConfidenceMeter level={report.true_engagement.confidence} />
                <p className="text-[10px] font-mono text-slate-400 border-l border-white/10 pl-6">
                    Sample Size: {report.epistemic_state.data_points_analyzed} pts
                    <span className="mx-2 text-slate-600">|</span>
                    Status: <span className={report.epistemic_state.status === 'ROBUST' ? 'text-green-400' : 'text-yellow-400'}>{report.epistemic_state.status}</span>
                </p>
            </div>
            <Link href="/methodology" className="text-[10px] text-slate-500 hover:text-white uppercase tracking-widest font-bold transition-colors">
                Methodology
            </Link>
        </div>

        {/* Profile Header */}
        <div className="p-8">
          {getWarningBanner(report)}

          <div className="glass-card rounded-xl p-6 flex flex-col md:flex-row justify-between items-center gap-6 border-l-4 border-l-blue-500 shadow-float">
            <div className="flex items-center gap-6">
              <div className="relative">
                <div className="w-24 h-24 rounded-full border-2 border-slate-600 p-1">
                  <div className="w-full h-full rounded-full bg-slate-800 flex items-center justify-center text-3xl font-bold text-white/20">
                    {report.handle.charAt(0).toUpperCase()}
                  </div>
                </div>
              </div>
              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <h2 className="text-3xl font-black tracking-tight">{report.handle}</h2>
                  <div className="flex gap-1.5">
                    <span className="px-2 py-0.5 rounded bg-white/5 text-[10px] font-bold text-white/60 border border-white/10 uppercase">{report.platform}</span>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-white/50 text-sm">
                  <span className="flex items-center gap-1.5"><span className="material-symbols-outlined text-[16px] text-blue-400">schedule</span> Scanned {new Date(report.generated_at).toLocaleTimeString()}</span>
                  <span className="flex items-center gap-1.5"><span className="material-symbols-outlined text-[16px]">location_on</span> Global</span>
                </div>
              </div>
            </div>
            <button onClick={() => window.location.reload()} className="bg-white/5 hover:bg-white/10 border border-white/10 px-6 py-2.5 rounded-lg text-sm font-bold transition-all flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">refresh</span> Refresh Live Data
            </button>
          </div>

          {/* 4-Pillar Scores (Refactored for Uncertainty) */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
            {[
                { 
                    title: "Signal Consistency", 
                    score: report.true_engagement.signal_strength, 
                    confidence: report.true_engagement.confidence,
                    history: report.true_engagement.history
                },
                { 
                    title: "Audience Patterns", 
                    score: report.audience_authenticity.signal_strength, 
                    confidence: report.audience_authenticity.confidence,
                    history: report.audience_authenticity.history
                },
                { 
                    title: "Brand Safety", 
                    score: report.brand_safety.signal_strength, 
                    confidence: report.brand_safety.confidence,
                    history: report.brand_safety.history
                },
                { 
                    title: "Niche Credibility", 
                    score: report.niche_credibility?.signal_strength ?? 0, 
                    confidence: report.niche_credibility?.confidence ?? 0,
                    history: report.niche_credibility?.history ?? []
                }
            ].map((metric, idx) => (
                <div key={idx} className="glass-card p-5 rounded-xl flex flex-col justify-between h-48 hover:border-blue-400/30 transition-colors group">
                    <div>
                        <UncertaintyBand 
                            score={metric.score} 
                            confidence={metric.confidence} 
                            label={metric.title} 
                        />
                    </div>

                    <div className="mt-auto">
                        <div className="flex justify-between items-end mb-2">
                            <p className="text-[10px] text-slate-400 font-medium">
                                CONFIDENCE: <span className={metric.confidence > 0.8 ? "text-blue-400" : "text-yellow-400"}>
                                    {(metric.confidence * 100).toFixed(0)}%
                                </span>
                            </p>
                        </div>
                        {/* Mini Sparkline */}
                        <div className="h-6 w-full flex items-end gap-[2px] opacity-50 group-hover:opacity-100 transition-opacity">
                            {metric.history.length > 0 ? metric.history.map((val, i) => (
                                <div key={i} className="bg-slate-500 w-full rounded-t-sm" style={{ height: `${val}%` }}></div>
                            )) : <div className="text-[10px] text-white/20 w-full text-center">No history</div>}
                        </div>
                        
                        {/* Micro-Footer for Screenshots */}
                        <div className="border-t border-white/5 mt-2 pt-1 flex justify-between items-center opacity-50">
                            <span className="text-[8px] font-mono text-slate-500">{report.methodology_version}</span>
                            <span className="text-[8px] font-mono text-slate-500">{new Date().toISOString().split('T')[0]}</span>
                        </div>
                    </div>
                </div>
            ))}
          </div>

          {/* Main Grid Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8 pb-10">
            {/* Left: Engagement Chart & Evidence Trail */}
            <div className="lg:col-span-2 space-y-8">
              {/* Engagement Breakdown Chart */}
              <div className="glass-card rounded-xl p-6">
                <div className="flex justify-between items-center mb-8">
                  <div>
                    <h4 className="text-lg font-bold">Engagement Breakdown</h4>
                    <p className="text-xs text-white/40">Technical line graph: Comment-to-Like Ratio</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-blue-400">
                        {report.true_engagement.history[report.true_engagement.history.length - 1]?.toFixed(1) || "N/A"}
                    </p>
                    <p className="text-[10px] text-slate-400 font-bold">
                        {report.true_engagement.benchmark_delta > 0 ? '+' : ''}{report.true_engagement.benchmark_delta.toFixed(1)}% vs BENCHMARK
                    </p>
                  </div>
                </div>
                <div className="h-64 w-full relative">
                  <svg className="w-full h-full preserve-3d" viewBox="0 0 1000 300">
                    <defs>
                      <linearGradient id="chartGradient" x1="0" x2="0" y1="0" y2="1">
                        <stop offset="0%" stopColor="#60a5fa" stopOpacity="0.3"></stop>
                        <stop offset="100%" stopColor="#60a5fa" stopOpacity="0"></stop>
                      </linearGradient>
                    </defs>
                    <path d={chartFill} fill="url(#chartGradient)"></path>
                    <path d={chartPath} fill="none" stroke="#60a5fa" strokeWidth="3"></path>
                  </svg>
                  <div className="absolute bottom-0 left-0 right-0 flex justify-between px-2 pt-4 border-t border-white/5">
                    <span className="text-[10px] font-bold text-white/30">PAST 6 MONTHS</span>
                    <span className="text-[10px] font-bold text-white/30">PRESENT</span>
                  </div>
                </div>
              </div>

              {/* Statistical Heuristics Section */}
              <div className="glass-card rounded-xl p-6">
                <h4 className="text-lg font-bold mb-6 flex items-center gap-2">
                  <span className="material-symbols-outlined text-blue-400">analytics</span>
                  Statistical Heuristics
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="text-white/30 border-b border-white/5 uppercase text-[10px] tracking-widest font-bold">
                        <th className="pb-4">Metric Heuristic</th>
                        <th className="pb-4">Current Value</th>
                        <th className="pb-4">Benchmark Delta</th>
                        <th className="pb-4">Stability</th>
                        <th className="pb-4 text-right">Methodology</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {report.profile_metrics.map((metric, i) => (
                        <tr key={i} className="group hover:bg-white/5 transition-colors">
                            <td className="py-4 font-bold text-white/80">{metric.name}</td>
                            <td className="py-4 text-blue-300 font-mono">{metric.value}</td>
                            <td className={`py-4 font-mono ${metric.delta.includes('-') ? 'text-purple-400' : 'text-slate-400'}`}>{metric.delta}</td>
                            <td className="py-4">
                            <div className="w-16 h-1 bg-white/10 rounded-full overflow-hidden">
                                <div className="h-full bg-blue-400" style={{ width: `${metric.stability * 100}%` }}></div>
                            </div>
                            </td>
                            <td className="py-4 text-right text-white/30"><span className="material-symbols-outlined text-[16px]">info</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
            
            {/* Right Column: Evidence Trail */}
            <div className="space-y-6">
               <h3 className="text-lg font-bold flex items-center gap-2">
                 <span className="material-symbols-outlined text-blue-400">gavel</span>
                 Evidence Trail
               </h3>
               <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-2">Sample, not exhaustive</p>
               <div className="glass-card p-4 rounded-xl space-y-4 max-h-[800px] overflow-y-auto">
                  {/* Evidence Items */}
                  {report.evidence_vault.length > 0 ? (
                    report.evidence_vault.map((item) => (
                      <EvidenceCard 
                        key={item.evidence_id} 
                        item={{
                            id: item.evidence_id,
                            type: item.type as any, // Cast to match EvidenceItem type
                            content: item.excerpt,
                            timestamp: item.timestamp,
                            sourceUrl: item.source_url,
                            severity: 'medium', // Default to medium for now, logic can be added later
                        }} 
                      />
                    ))
                  ) : (
                    <div className="text-center py-12 text-white/30 text-xs flex flex-col items-center gap-3">
                        <span className="material-symbols-outlined text-4xl opacity-20">search_off</span>
                        No public evidence found in this scan.
                    </div>
                  )}
               </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
