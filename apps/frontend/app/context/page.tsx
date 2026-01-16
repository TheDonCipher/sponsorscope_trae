import { Navbar } from '../../components/Navbar';

export default function ResearchContext() {
  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark text-[#101816] dark:text-white font-display">
      <Navbar />
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="mb-8">
            <span className="text-primary text-sm font-bold tracking-widest uppercase">Active Calibration</span>
            <h1 className="text-4xl font-bold mt-2">North American Lifestyle Vertical (Q3 2024)</h1>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Baseline Engagement</h3>
                <p className="text-3xl font-bold text-primary">2.4%</p>
                <p className="text-sm text-slate-500 mt-2">Average per post</p>
            </div>
            <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Bot Tolerance</h3>
                <p className="text-3xl font-bold text-yellow-500">15%</p>
                <p className="text-sm text-slate-500 mt-2">Max acceptable threshold</p>
            </div>
            <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-2">Sample Size</h3>
                <p className="text-3xl font-bold text-blue-500">14.2M</p>
                <p className="text-sm text-slate-500 mt-2">Profiles analyzed</p>
            </div>
        </div>

        <div className="prose dark:prose-invert max-w-none">
            <h2>Scope of Analysis</h2>
            <p>
                This context defines the benchmarks used to calculate "Niche Credibility" and "True Engagement" scores.
                We analyze creators who primarily post about fashion, travel, home decor, and daily life in the United States and Canada.
            </p>
            
            <h3>Inclusion Criteria</h3>
            <ul>
                <li><strong>Geography:</strong> >60% audience location in US/Canada.</li>
                <li><strong>Language:</strong> English (primary).</li>
                <li><strong>Content:</strong> Visual-first lifestyle content (verified via computer vision tags).</li>
                <li><strong>Follower Count:</strong> 10k - 5M.</li>
            </ul>

            <h3>Why Context Matters</h3>
            <p>
                A 2% engagement rate is excellent for a macro-influencer (1M+ followers) but poor for a nano-influencer (5k followers).
                Similarly, "Gaming" audiences behave differently than "Beauty" audiences.
                By locking the Research Context to <strong>North American Lifestyle</strong>, we ensure that scores are relative to <em>peers</em>, not the entire internet.
            </p>
        </div>
      </div>
    </div>
  );
}
