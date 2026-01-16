import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useReport } from '../../hooks/useReport';

interface ReportViewProps {
  handle: string;
}

export const ReportView: React.FC<ReportViewProps> = ({ handle }) => {
  const { report, loading, error } = useReport(handle);
  const [loadingStep, setLoadingStep] = useState(0);
  
  const loadingSteps = [
    "INITIALIZING NEURAL SCAN...",
    "CONNECTING TO INSTAGRAM NODE...",
    "EXTRACTING ENGAGEMENT SIGNALS...",
    "VERIFYING AUDIENCE AUTHENTICITY...",
    "CALCULATING BRAND SAFETY SCORE...",
    "FINALIZING REPORT..."
  ];

  useEffect(() => {
    if (loading) {
      const interval = setInterval(() => {
        setLoadingStep((prev) => (prev + 1) % loadingSteps.length);
      }, 800); // Change text every 800ms
      return () => clearInterval(interval);
    } else {
      setLoadingStep(0);
    }
  }, [loading]);

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen bg-background-dark text-white">
      <div className="flex flex-col items-center gap-6">
        <div className="relative">
            <div className="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-8 h-8 bg-primary/10 rounded-full animate-pulse"></div>
            </div>
        </div>
        <div className="text-center">
            <p className="animate-pulse font-mono text-primary font-bold tracking-widest text-sm mb-2">{loadingSteps[loadingStep]}</p>
            <p className="text-xs text-white/40 font-mono">TARGET: @{handle}</p>
        </div>
        
        {/* Terminal-like log output */}
        <div className="w-64 h-24 bg-black/50 rounded-lg border border-white/10 p-3 overflow-hidden mt-4">
            <div className="space-y-1 font-mono text-[10px] text-green-500/80">
                <p>&gt; sys.init_sequence(target="{handle}")</p>
                <p className="opacity-80">&gt; verifying_integrity... OK</p>
                <p className="opacity-60">&gt; establishing_uplink... OK</p>
                <p className="opacity-40 animate-pulse">&gt; streaming_data...</p>
            </div>
        </div>
      </div>
    </div>
  );
  
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

  return (
    <div className="flex h-screen overflow-hidden bg-background-dark text-white font-grotesk selection:bg-neon-lime selection:text-black">
      {/* Sidebar Navigation */}
      <aside className="w-72 flex-shrink-0 flex flex-col border-r border-white/10 bg-background-dark/50 backdrop-blur-xl hidden lg:flex">
        <div className="p-6 flex flex-col h-full">
          {/* Logo Section */}
          <div className="flex items-center gap-3 mb-10">
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
            <Link href="/settings" className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors cursor-pointer group">
              <span className="material-symbols-outlined text-[20px] text-white/60 group-hover:text-white">settings</span>
              <p className="text-sm font-medium text-white/70 group-hover:text-white">Settings</p>
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
        {/* Profile Header */}
        <div className="p-8">
          <div className="glass-card rounded-xl p-6 flex flex-col md:flex-row justify-between items-center gap-6 border-l-4 border-l-neon-lime shadow-float">
            <div className="flex items-center gap-6">
              <div className="relative">
                <div className="w-24 h-24 rounded-full border-2 border-neon-lime/30 p-1">
                  <div className="w-full h-full rounded-full bg-slate-700 flex items-center justify-center text-3xl font-bold text-white/20">
                    {report.handle.charAt(0).toUpperCase()}
                  </div>
                </div>
                <div className="absolute -bottom-1 -right-1 bg-black rounded-full p-1.5 border border-white/10">
                   <span className="material-symbols-outlined text-white text-[16px]">verified</span>
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
                  <span className="flex items-center gap-1.5"><span className="material-symbols-outlined text-[16px] text-neon-lime">schedule</span> Scanned {new Date(report.generated_at).toLocaleTimeString()}</span>
                  <span className="flex items-center gap-1.5"><span className="material-symbols-outlined text-[16px]">location_on</span> Global</span>
                </div>
              </div>
            </div>
            <button className="bg-white/5 hover:bg-white/10 border border-white/10 px-6 py-2.5 rounded-lg text-sm font-bold transition-all flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px]">refresh</span> Refresh Live Data
            </button>
          </div>

          {/* 4-Pillar Scores */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
            {/* Score Card 1: True Engagement */}
            <div className="glass-card p-5 rounded-xl flex flex-col justify-between h-48 group hover:border-neon-lime/30 transition-colors">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-[10px] uppercase tracking-[0.2em] text-white/40 font-bold mb-1">True Engagement</p>
                  <h3 className="text-4xl font-black text-neon-lime">{report.true_engagement.signal_strength.toFixed(0)}%</h3>
                </div>
                <div className="w-12 h-12 relative">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle className="text-white/5" cx="24" cy="24" fill="transparent" r="20" stroke="currentColor" strokeWidth="3"></circle>
                    <circle className="text-neon-lime" cx="24" cy="24" fill="transparent" r="20" stroke="currentColor" strokeDasharray="125.6" strokeDashoffset={125.6 - (125.6 * report.true_engagement.signal_strength / 100)} strokeWidth="3"></circle>
                  </svg>
                </div>
              </div>
              <div className="mt-auto">
                <p className="text-[10px] text-white/40 mb-2 font-medium">CONFIDENCE: {(report.true_engagement.confidence * 100).toFixed(0)}%</p>
                <div className="h-6 w-full flex items-end gap-[2px]">
                   {report.true_engagement.history.map((val, i) => (
                      <div key={i} className={`bg-neon-lime/${20 + i*10} w-full rounded-t-sm`} style={{ height: `${val}%` }}></div>
                   ))}
                </div>
              </div>
            </div>

            {/* Score Card 2: Audience Authenticity */}
            <div className="glass-card p-5 rounded-xl flex flex-col justify-between h-48 hover:border-neon-lime/30 transition-colors">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-[10px] uppercase tracking-[0.2em] text-white/40 font-bold mb-1">Audience Authenticity</p>
                  <h3 className="text-4xl font-black text-neon-lime">{report.audience_authenticity.signal_strength.toFixed(0)}%</h3>
                </div>
                <div className="w-12 h-12 relative">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle className="text-white/5" cx="24" cy="24" fill="transparent" r="20" stroke="currentColor" strokeWidth="3"></circle>
                    <circle className="text-neon-lime" cx="24" cy="24" fill="transparent" r="20" stroke="currentColor" strokeDasharray="125.6" strokeDashoffset={125.6 - (125.6 * report.audience_authenticity.signal_strength / 100)} strokeWidth="3"></circle>
                  </svg>
                </div>
              </div>
              <div className="mt-auto">
                <p className="text-[10px] text-white/40 mb-2 font-medium">CONFIDENCE: {(report.audience_authenticity.confidence * 100).toFixed(0)}%</p>
                <div className="h-6 w-full flex items-end gap-[2px]">
                   {report.audience_authenticity.history.map((val, i) => (
                      <div key={i} className={`bg-neon-lime/${20 + i*10} w-full rounded-t-sm`} style={{ height: `${val}%` }}></div>
                   ))}
                </div>
              </div>
            </div>

            {/* Score Card 3: Brand Safety */}
            <div className="glass-card p-5 rounded-xl flex flex-col justify-between h-48 border-b-2 border-b-neon-lime/30 hover:bg-white/5 transition-colors">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-[10px] uppercase tracking-[0.2em] text-white/40 font-bold mb-1">Brand Safety</p>
                  <h3 className="text-4xl font-black text-neon-lime">{report.brand_safety.signal_strength.toFixed(0)}%</h3>
                </div>
                <div className="w-12 h-12 relative">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle className="text-white/5" cx="24" cy="24" fill="transparent" r="20" stroke="currentColor" strokeWidth="3"></circle>
                    <circle className="text-neon-lime" cx="24" cy="24" fill="transparent" r="20" stroke="currentColor" strokeDasharray="125.6" strokeDashoffset={125.6 - (125.6 * report.brand_safety.signal_strength / 100)} strokeWidth="3"></circle>
                  </svg>
                </div>
              </div>
              <div className="mt-auto">
                <p className="text-[10px] text-white/40 mb-2 font-medium">CONFIDENCE: {(report.brand_safety.confidence * 100).toFixed(0)}%</p>
                <div className="h-6 w-full flex items-end gap-[2px]">
                   {report.brand_safety.history.map((val, i) => (
                      <div key={i} className={`bg-neon-lime/${20 + i*10} w-full rounded-t-sm`} style={{ height: `${val}%` }}></div>
                   ))}
                </div>
              </div>
            </div>

            {/* Score Card 4: Niche Credibility */}
            <div className="glass-card p-5 rounded-xl flex flex-col justify-between h-48 hover:border-neon-lime/30 transition-colors">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-[10px] uppercase tracking-[0.2em] text-white/40 font-bold mb-1">Niche Credibility</p>
                  <h3 className="text-4xl font-black text-neon-lime">{report.niche_credibility?.signal_strength.toFixed(0) ?? "N/A"}%</h3>
                </div>
                <div className="w-12 h-12 relative">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle className="text-white/5" cx="24" cy="24" fill="transparent" r="20" stroke="currentColor" strokeWidth="3"></circle>
                    <circle className="text-neon-lime" cx="24" cy="24" fill="transparent" r="20" stroke="currentColor" strokeDasharray="125.6" strokeDashoffset={125.6 - (125.6 * (report.niche_credibility?.signal_strength ?? 0) / 100)} strokeWidth="3"></circle>
                  </svg>
                </div>
              </div>
              <div className="mt-auto">
                <p className="text-[10px] text-white/40 mb-2 font-medium">CONFIDENCE: {(report.niche_credibility?.confidence ?? 0 * 100).toFixed(0)}%</p>
                <div className="h-6 w-full flex items-end gap-[2px]">
                   {report.niche_credibility?.history.map((val, i) => (
                      <div key={i} className={`bg-neon-lime/${20 + i*10} w-full rounded-t-sm`} style={{ height: `${val}%` }}></div>
                   )) || <div className="text-[10px] text-white/20">No history</div>}
                </div>
              </div>
            </div>
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
                    <p className="text-2xl font-bold text-neon-lime">
                        {report.true_engagement.history[report.true_engagement.history.length - 1]?.toFixed(1) || "N/A"}
                    </p>
                    <p className="text-[10px] text-green-400 font-bold">
                        {report.true_engagement.benchmark_delta > 0 ? '+' : ''}{report.true_engagement.benchmark_delta.toFixed(1)}% vs BENCHMARK
                    </p>
                  </div>
                </div>
                <div className="h-64 w-full relative">
                  <svg className="w-full h-full preserve-3d" viewBox="0 0 1000 300">
                    <defs>
                      <linearGradient id="chartGradient" x1="0" x2="0" y1="0" y2="1">
                        <stop offset="0%" stopColor="#bfff00" stopOpacity="0.3"></stop>
                        <stop offset="100%" stopColor="#bfff00" stopOpacity="0"></stop>
                      </linearGradient>
                    </defs>
                    <path d={chartFill} fill="url(#chartGradient)"></path>
                    <path d={chartPath} fill="none" stroke="#bfff00" strokeWidth="3"></path>
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
                  <span className="material-symbols-outlined text-neon-lime">analytics</span>
                  Statistical Heuristics
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="text-white/30 border-b border-white/5 uppercase text-[10px] tracking-widest font-bold">
                        <th className="pb-4">Metric Heuristic</th>
                        <th className="pb-4">Current Score</th>
                        <th className="pb-4">Benchmark Delta</th>
                        <th className="pb-4">Stability</th>
                        <th className="pb-4 text-right">Methodology</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {report.profile_metrics.map((metric, i) => (
                        <tr key={i} className="group hover:bg-white/5 transition-colors">
                            <td className="py-4 font-bold text-white/80">{metric.name}</td>
                            <td className="py-4 text-neon-lime font-mono">{metric.value}</td>
                            <td className={`py-4 font-mono ${metric.delta.includes('-') ? 'text-red-400' : 'text-green-400'}`}>{metric.delta}</td>
                            <td className="py-4">
                            <div className="w-16 h-1 bg-white/10 rounded-full overflow-hidden">
                                <div className="h-full bg-neon-lime" style={{ width: `${metric.stability * 100}%` }}></div>
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
               <h3 className="text-lg font-bold">Evidence Trail</h3>
               <div className="glass-card p-4 rounded-xl space-y-4">
                  {/* Mock Evidence Items */}
                  {report.evidence_vault.length > 0 ? (
                    report.evidence_vault.map((item) => (
                      <div key={item.evidence_id} className="p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer border border-white/5">
                          <div className="flex justify-between items-start mb-2">
                              <span className="text-xs font-bold text-white/60 line-clamp-1">{item.excerpt || "Evidence item"}</span>
                              <span className="text-[10px] text-white/40 whitespace-nowrap ml-2">{new Date(item.timestamp).toLocaleTimeString()}</span>
                          </div>
                          <div className="flex items-center gap-2 mt-2">
                              <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-[10px] font-bold rounded uppercase">{item.type}</span>
                              <span className="text-neon-lime text-[10px] flex items-center gap-1 ml-auto hover:underline" onClick={() => window.open(item.source_url, '_blank')}>
                                VIEW SOURCE <span className="material-symbols-outlined text-[10px]">open_in_new</span>
                              </span>
                          </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-white/30 text-xs">
                        No public evidence found.
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
