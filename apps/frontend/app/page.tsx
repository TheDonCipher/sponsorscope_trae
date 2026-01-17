"use client";

import { useState } from 'react';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [searchHandle, setSearchHandle] = useState('');
  const router = useRouter();

  const handleSearch = () => {
    if (searchHandle) {
      // Basic validation: remove @ if present
      const cleanHandle = searchHandle.replace('@', '').trim();
      if (cleanHandle) {
        router.push(`/report/${cleanHandle}`);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <main className="flex flex-col min-h-screen bg-background-light dark:bg-background-dark text-[#101816] dark:text-white font-display overflow-x-hidden antialiased">
      {/* Top Navigation */}
      
      {/* Hero Section */}
      <section className="relative pt-16 pb-12 sm:pt-24 sm:pb-20 lg:pb-24 overflow-hidden">
        {/* Background Decoration */}
        <div className="absolute inset-0 -z-10 opacity-30 dark:opacity-20 pointer-events-none" style={{ backgroundImage: 'radial-gradient(#cbd5e1 1px, transparent 1px)', backgroundSize: '24px 24px' }}></div>
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-7xl -z-10 bg-gradient-to-b from-transparent via-primary/5 to-transparent"></div>
        
        <div className="layout-content-container max-w-[960px] mx-auto px-4 flex flex-col items-center text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 border border-border-light dark:border-border-dark mb-6">
            <span className="flex size-2 rounded-full bg-primary animate-pulse"></span>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-600 dark:text-slate-300">Live System v2.4</span>
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-[#101816] dark:text-white mb-6 leading-[1.1]">
            The operating system for <br className="hidden sm:block"/>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-emerald-600 dark:to-emerald-400">influencer vetting.</span>
          </h1>
          <p className="text-lg sm:text-xl text-slate-600 dark:text-slate-400 max-w-2xl mb-10 leading-relaxed">
            Real-time analysis on engagement, authenticity, and brand safety. 
            Institutional-grade data for modern marketing teams.
          </p>

          {/* Search Component */}
          <div className="w-full max-w-[560px] relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-primary to-emerald-400 rounded-xl opacity-20 group-hover:opacity-40 blur transition duration-200"></div>
            <div className="relative flex items-center w-full h-14 sm:h-16 bg-surface-light dark:bg-surface-dark rounded-xl border border-border-light dark:border-border-dark shadow-xl overflow-hidden">
              <div className="pl-5 text-slate-400 dark:text-slate-500">
                <span className="material-symbols-outlined">search</span>
              </div>
              <input 
                className="w-full h-full bg-transparent border-none focus:ring-0 text-[#101816] dark:text-white placeholder-slate-400 text-base sm:text-lg px-4 focus:outline-none" 
                placeholder="e.g., @mkbhd, @charli_damilio..." 
                type="text"
                value={searchHandle}
                onChange={(e) => setSearchHandle(e.target.value)}
                onKeyDown={handleKeyDown}
              />
              <div className="pr-2">
                <button 
                  onClick={handleSearch}
                  className="h-10 sm:h-12 px-6 rounded-lg bg-primary hover:bg-emerald-400 text-[#101816] font-bold text-sm transition-colors"
                >
                  Analyze
                </button>
              </div>
            </div>
          </div>

          {/* Chips */}
          <div className="flex flex-wrap justify-center gap-3 mt-8">
            <button className="flex items-center gap-2 px-4 py-2 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-primary/50 transition-colors shadow-sm">
              <span className="material-symbols-outlined text-xl text-pink-600">photo_camera</span>
              <span className="text-sm font-medium">Instagram</span>
            </button>
            <button className="flex items-center gap-2 px-4 py-2 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-primary/50 transition-colors shadow-sm">
              <span className="material-symbols-outlined text-xl text-[#101816] dark:text-white">music_note</span>
              <span className="text-sm font-medium">TikTok</span>
            </button>
            <button className="flex items-center gap-2 px-4 py-2 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-primary/50 transition-colors shadow-sm">
              <span className="material-symbols-outlined text-xl text-red-600">play_arrow</span>
              <span className="text-sm font-medium">YouTube</span>
            </button>
          </div>
        </div>
      </section>

      {/* Live Intelligence Dashboard - REMOVED */}
      <section className="bg-slate-50 dark:bg-[#151a23] py-16 border-t border-border-light dark:border-border-dark hidden">
        <div className="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 gap-4">
            <div>
              <h2 className="text-2xl font-bold text-[#101816] dark:text-white flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                Live Intelligence Feed
              </h2>
              <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Real-time data processing from global nodes.</p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs font-mono text-slate-500 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-2 py-1 rounded">API_LATENCY: 42ms</span>
              <span className="text-xs font-mono text-primary bg-primary/10 border border-primary/20 px-2 py-1 rounded">SYSTEM: ONLINE</span>
            </div>
          </div>

          {/* 4-Pillar Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Card 1: Engagement (Sparkline) */}
            <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark shadow-sm hover:shadow-md transition-shadow group">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">True Engagement</p>
                  <h3 className="text-3xl font-bold text-[#101816] dark:text-white mt-1">8.4<span className="text-lg text-slate-400 font-medium">/10</span></h3>
                </div>
                <div className="p-2 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg text-emerald-600 dark:text-emerald-400">
                  <span className="material-symbols-outlined">trending_up</span>
                </div>
              </div>
              <div className="h-16 w-full mb-4">
                <svg className="w-full h-full overflow-visible" viewBox="0 0 100 40">
                  <defs>
                    <linearGradient id="gradient" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="#00c78b" stopOpacity="0.2"></stop>
                      <stop offset="100%" stopColor="#00c78b" stopOpacity="0"></stop>
                    </linearGradient>
                  </defs>
                  <path d="M0,40 L0,30 L10,25 L20,32 L30,15 L40,20 L50,10 L60,25 L70,20 L80,10 L90,15 L100,5" fill="url(#gradient)" stroke="none"></path>
                  <path d="M0,30 L10,25 L20,32 L30,15 L40,20 L50,10 L60,25 L70,20 L80,10 L90,15 L100,5" fill="none" stroke="#00c78b" strokeWidth="2" vectorEffect="non-scaling-stroke"></path>
                  <circle className="animate-pulse" cx="100" cy="5" fill="#00c78b" r="3"></circle>
                </svg>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-emerald-600 font-semibold">+12.5%</span>
                <span className="text-slate-500">vs 30d avg</span>
              </div>
            </div>

            {/* Card 2: Authenticity (Gauge) */}
            <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark shadow-sm hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Audience Quality</p>
                <span className="material-symbols-outlined text-slate-400 text-lg">verified_user</span>
              </div>
              <div className="flex flex-col items-center justify-center py-4">
                <div className="relative size-28 rounded-full bg-slate-100 dark:bg-slate-800" style={{ background: 'conic-gradient(#00c78b 0% 78%, #e2e8f0 78% 100%)' }}>
                  <div className="absolute inset-2 bg-surface-light dark:bg-surface-dark rounded-full flex flex-col items-center justify-center">
                    <span className="text-2xl font-bold text-[#101816] dark:text-white">78%</span>
                    <span className="text-xs text-slate-500 uppercase">Authentic</span>
                  </div>
                </div>
              </div>
              <div className="flex justify-between items-center text-sm border-t border-dashed border-slate-200 dark:border-slate-700 pt-3 mt-1">
                <span className="text-slate-500">Suspicious</span>
                <span className="font-mono text-[#101816] dark:text-white">12.4%</span>
              </div>
            </div>

             {/* Card 3: Brand Safety (Shield) */}
             <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark shadow-sm hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Brand Safety</p>
                  <h3 className="text-3xl font-bold text-[#101816] dark:text-white mt-1">98<span className="text-lg text-slate-400 font-medium">%</span></h3>
                </div>
                <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-blue-600 dark:text-blue-400">
                  <span className="material-symbols-outlined">shield</span>
                </div>
              </div>
              <div className="space-y-3 mt-2">
                <div className="flex items-center gap-3 text-sm">
                  <span className="material-symbols-outlined text-green-500 text-lg">check_circle</span>
                  <span className="text-slate-600 dark:text-slate-300">No hate speech detected</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <span className="material-symbols-outlined text-green-500 text-lg">check_circle</span>
                  <span className="text-slate-600 dark:text-slate-300">Competitor clean</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                  <span className="material-symbols-outlined text-slate-400 text-lg">remove_circle_outline</span>
                  <span className="text-slate-500">Political content (Low)</span>
                </div>
              </div>
            </div>

            {/* Card 4: Niche (Badge) */}
            <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark shadow-sm hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Niche Authority</p>
                  <h3 className="text-xl font-bold text-[#101816] dark:text-white mt-1 truncate">Tech & Gadgets</h3>
                </div>
                <div className="p-2 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-purple-600 dark:text-purple-400">
                  <span className="material-symbols-outlined">workspace_premium</span>
                </div>
              </div>
              <div className="flex items-center justify-center py-2">
                <div className="bg-gradient-to-br from-purple-500 to-indigo-600 text-white px-4 py-2 rounded-lg shadow-lg text-center transform rotate-2 hover:rotate-0 transition-transform">
                    <p className="text-xs font-bold uppercase opacity-80">Rank</p>
                    <p className="text-2xl font-black">Top 5%</p>
                </div>
              </div>
              <p className="text-center text-xs text-slate-500 mt-4">Among 14.2M profiles in vertical</p>
            </div>
          </div>
        </div>
      </section>

      {/* Methodology Section */}
      <section className="py-24 bg-surface-light dark:bg-surface-dark border-t border-border-light dark:border-border-dark">
        <div className="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl font-bold text-[#101816] dark:text-white mb-4">Deep Tech Methodology</h2>
            <p className="text-slate-600 dark:text-slate-400">
              Our analysis pipeline combines graph theory, heuristic scoring, and large language models to provide a holistic view of influencer credibility.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl bg-slate-50 dark:bg-[#151a23] border border-border-light dark:border-border-dark">
              <div className="size-12 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-4">
                <span className="material-symbols-outlined text-2xl">hub</span>
              </div>
              <h3 className="text-xl font-bold text-[#101816] dark:text-white mb-2">Graph Analysis</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                We map connection reciprocity and reuse patterns to identify artificial engagement networks and pod activity.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 dark:bg-[#151a23] border border-border-light dark:border-border-dark">
              <div className="size-12 rounded-lg bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-4">
                <span className="material-symbols-outlined text-2xl">psychology</span>
              </div>
              <h3 className="text-xl font-bold text-[#101816] dark:text-white mb-2">LLM Refinement</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                Contextual understanding of content safety using advanced LLMs to detect hate speech, political bias, and brand risks.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-50 dark:bg-[#151a23] border border-border-light dark:border-border-dark">
              <div className="size-12 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-4">
                <span className="material-symbols-outlined text-2xl">policy</span>
              </div>
              <h3 className="text-xl font-bold text-[#101816] dark:text-white mb-2">Governance & Ethics</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                Automated ethical reviews and killswitches ensure data integrity and compliance with platform policies.
              </p>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </main>
  );
}
