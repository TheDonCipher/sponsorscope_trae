import { Navbar } from '../../components/Navbar';
import { Footer } from '../../components/Footer';

export default function Pricing() {
  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark text-[#101816] dark:text-white font-display">
      <div className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">Transparent Pricing for Modern Vetting</h1>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Choose the plan that fits your agency's scale. No hidden fees, no long-term contracts for pilots.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Starter */}
          <div className="bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-2xl p-8 flex flex-col">
            <h3 className="text-xl font-bold mb-2">Starter</h3>
            <div className="flex items-baseline gap-1 mb-6">
              <span className="text-4xl font-bold">$49</span>
              <span className="text-slate-500">/mo</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 mb-8 text-sm">Perfect for freelance marketers and small teams.</p>
            <ul className="space-y-4 mb-8 flex-1">
              <li className="flex items-center gap-2 text-sm"><span className="material-symbols-outlined text-green-500 text-lg">check</span> 50 Reports / month</li>
              <li className="flex items-center gap-2 text-sm"><span className="material-symbols-outlined text-green-500 text-lg">check</span> Instagram & TikTok Support</li>
              <li className="flex items-center gap-2 text-sm"><span className="material-symbols-outlined text-green-500 text-lg">check</span> Basic PDF Exports</li>
            </ul>
            <button className="w-full py-3 rounded-lg border border-border-light dark:border-border-dark font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">Start Trial</button>
          </div>

          {/* Pro */}
          <div className="bg-surface-light dark:bg-surface-dark border-2 border-primary rounded-2xl p-8 flex flex-col relative shadow-2xl shadow-primary/10">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-primary text-[#101816] px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide">Most Popular</div>
            <h3 className="text-xl font-bold mb-2">Agency Pro</h3>
            <div className="flex items-baseline gap-1 mb-6">
              <span className="text-4xl font-bold">$199</span>
              <span className="text-slate-500">/mo</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 mb-8 text-sm">For growing agencies needing deep insights.</p>
            <ul className="space-y-4 mb-8 flex-1">
              <li className="flex items-center gap-2 text-sm"><span className="material-symbols-outlined text-green-500 text-lg">check</span> 500 Reports / month</li>
              <li className="flex items-center gap-2 text-sm"><span className="material-symbols-outlined text-green-500 text-lg">check</span> Advanced Heuristics (Bot Detection)</li>
              <li className="flex items-center gap-2 text-sm"><span className="material-symbols-outlined text-green-500 text-lg">check</span> White-label PDF Exports</li>
              <li className="flex items-center gap-2 text-sm"><span className="material-symbols-outlined text-green-500 text-lg">check</span> Priority Support</li>
            </ul>
            <button className="w-full py-3 rounded-lg bg-primary hover:bg-emerald-400 text-[#101816] font-bold transition-colors shadow-lg shadow-primary/20">Get Started</button>
          </div>

          {/* Enterprise */}
          <div className="bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-2xl p-8 flex flex-col">
            <h3 className="text-xl font-bold mb-2">Enterprise</h3>
            <div className="flex items-baseline gap-1 mb-6">
              <span className="text-4xl font-bold">Custom</span>
            </div>
            <p className="text-slate-600 dark:text-slate-400 mb-8 text-sm">Full API access and custom integrations.</p>
            <ul className="space-y-4 mb-8 flex-1">
              <li className="flex items-center gap-2 text-sm"><span className="material-symbols-outlined text-green-500 text-lg">check</span> Unlimited Reports</li>
              <li className="flex items-center gap-2 text-sm"><span className="material-symbols-outlined text-green-500 text-lg">check</span> Full API Access</li>
              <li className="flex items-center gap-2 text-sm"><span className="material-symbols-outlined text-green-500 text-lg">check</span> Custom Graph Analysis</li>
              <li className="flex items-center gap-2 text-sm"><span className="material-symbols-outlined text-green-500 text-lg">check</span> Dedicated Success Manager</li>
            </ul>
            <button className="w-full py-3 rounded-lg border border-border-light dark:border-border-dark font-bold hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">Contact Sales</button>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
