import { Navbar } from '../../components/Navbar';

import { Footer } from '../../components/Footer';

export default function Settings() {
  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark text-[#101816] dark:text-white font-display">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <h1 className="text-3xl font-bold mb-8">Settings</h1>

        <div className="space-y-8">
            {/* API Keys */}
            <section className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h2 className="text-xl font-bold">API Keys</h2>
                        <p className="text-sm text-slate-500">Manage your secret keys for API access.</p>
                    </div>
                    <button className="bg-primary/10 text-primary px-4 py-2 rounded-lg text-sm font-bold hover:bg-primary/20 transition-colors">
                        Generate New Key
                    </button>
                </div>
                <div className="bg-slate-900 rounded-lg p-3 flex items-center justify-between">
                    <code className="text-slate-400 font-mono text-sm">sk_live_****************28x9</code>
                    <span className="material-symbols-outlined text-slate-500 cursor-pointer hover:text-white">content_copy</span>
                </div>
            </section>

            {/* Notifications */}
            <section className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark">
                <h2 className="text-xl font-bold mb-4">Notifications</h2>
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium">Scan Completion</p>
                            <p className="text-sm text-slate-500">Receive an email when a large report is ready.</p>
                        </div>
                        <div className="w-11 h-6 bg-primary rounded-full relative cursor-pointer">
                            <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div>
                        </div>
                    </div>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="font-medium">Weekly Digest</p>
                            <p className="text-sm text-slate-500">Summary of all creators analyzed this week.</p>
                        </div>
                        <div className="w-11 h-6 bg-slate-700 rounded-full relative cursor-pointer">
                            <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full"></div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Profile */}
            <section className="bg-surface-light dark:bg-surface-dark p-6 rounded-xl border border-border-light dark:border-border-dark">
                <h2 className="text-xl font-bold mb-4">Organization Profile</h2>
                <div className="grid gap-4">
                    <div>
                        <label className="block text-sm font-medium mb-1 text-slate-500">Organization Name</label>
                        <input type="text" className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-4 py-2" defaultValue="Acme Marketing" />
                    </div>
                    <div>
                        <label className="block text-sm font-medium mb-1 text-slate-500">Billing Email</label>
                        <input type="email" className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-4 py-2" defaultValue="finance@acme.com" />
                    </div>
                </div>
            </section>
        </div>
      </div>
      <Footer />
    </div>
  );
}
