import { Navbar } from '../../components/Navbar';

export default function HelpCenter() {
  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark text-[#101816] dark:text-white font-display">
      <Navbar />
      <div className="max-w-4xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-bold mb-8">Help Center</h1>

        <div className="relative mb-12">
            <span className="absolute left-4 top-3.5 material-symbols-outlined text-slate-400">search</span>
            <input 
                type="text" 
                placeholder="Search for answers..." 
                className="w-full pl-12 pr-4 py-3 rounded-xl bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark focus:outline-none focus:ring-2 focus:ring-primary"
            />
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-12">
            <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark hover:border-primary transition-colors cursor-pointer">
                <span className="material-symbols-outlined text-3xl text-primary mb-4">school</span>
                <h3 className="text-xl font-bold mb-2">Getting Started</h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm">Learn the basics of running your first scan and interpreting results.</p>
            </div>
            <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark hover:border-primary transition-colors cursor-pointer">
                <span className="material-symbols-outlined text-3xl text-primary mb-4">credit_card</span>
                <h3 className="text-xl font-bold mb-2">Billing & Plans</h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm">Manage your subscription, payment methods, and invoices.</p>
            </div>
            <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark hover:border-primary transition-colors cursor-pointer">
                <span className="material-symbols-outlined text-3xl text-primary mb-4">api</span>
                <h3 className="text-xl font-bold mb-2">API Integration</h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm">Technical guides for integrating SponsorScope into your workflow.</p>
            </div>
            <div className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark hover:border-primary transition-colors cursor-pointer">
                <span className="material-symbols-outlined text-3xl text-primary mb-4">support_agent</span>
                <h3 className="text-xl font-bold mb-2">Contact Support</h3>
                <p className="text-slate-600 dark:text-slate-400 text-sm">Get in touch with our team for personalized assistance.</p>
            </div>
        </div>

        <section>
            <h2 className="text-2xl font-bold mb-6">Frequently Asked Questions</h2>
            <div className="space-y-4">
                <details className="bg-surface-light dark:bg-surface-dark p-4 rounded-lg border border-border-light dark:border-border-dark group">
                    <summary className="font-bold cursor-pointer flex justify-between items-center">
                        What does "Low Confidence" mean?
                        <span className="material-symbols-outlined transition-transform group-open:rotate-180">expand_more</span>
                    </summary>
                    <p className="mt-4 text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                        Low Confidence (0-59) indicates that our algorithms detected significant anomalies in the data. This could be due to engagement pods, bot activity, or highly irregular posting schedules. We recommend a manual review before proceeding with any sponsorship.
                    </p>
                </details>
                <details className="bg-surface-light dark:bg-surface-dark p-4 rounded-lg border border-border-light dark:border-border-dark group">
                    <summary className="font-bold cursor-pointer flex justify-between items-center">
                        Can I scan private accounts?
                        <span className="material-symbols-outlined transition-transform group-open:rotate-180">expand_more</span>
                    </summary>
                    <p className="mt-4 text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                        No. SponsorScope strictly adheres to privacy laws and platform terms of service. We only analyze publicly available data. Private accounts cannot be scanned.
                    </p>
                </details>
                <details className="bg-surface-light dark:bg-surface-dark p-4 rounded-lg border border-border-light dark:border-border-dark group">
                    <summary className="font-bold cursor-pointer flex justify-between items-center">
                        How often is data updated?
                        <span className="material-symbols-outlined transition-transform group-open:rotate-180">expand_more</span>
                    </summary>
                    <p className="mt-4 text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                        Reports are generated in real-time. Once generated, a report is cached for 24 hours to ensure speed. You can force a refresh on the dashboard if you need the absolute latest data.
                    </p>
                </details>
            </div>
        </section>
      </div>
    </div>
  );
}
