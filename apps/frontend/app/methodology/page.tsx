import { Footer } from '../../components/Footer';

export default function Methodology() {
  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark text-[#101816] dark:text-white font-display">
      <div className="max-w-4xl mx-auto px-6 py-12">
        <h1 className="text-4xl font-bold mb-2">SponsorScope Signal Overview</h1>
        <p className="text-sm text-slate-500 mb-8">Version 2.3 • Last Updated: 2026-01-16</p>

        <div className="space-y-12">
          <section>
            <h2 className="text-2xl font-bold mb-4 text-primary">What is the SponsorScope Signal?</h2>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-4">
              The <strong>SponsorScope Signal</strong> (formerly "Score") is a <strong>probabilistic credibility index</strong> ranging from 0 to 100. It estimates the likelihood that an influencer's audience engagement is organic, safe, and valuable for sponsors.
            </p>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-green-50 dark:bg-green-900/10 p-4 rounded-lg border border-green-100 dark:border-green-900/20">
                <h3 className="font-bold text-green-700 dark:text-green-400 mb-2">It IS:</h3>
                <ul className="list-disc list-inside text-sm text-slate-600 dark:text-slate-400 space-y-1">
                  <li>✅ A statistical estimate based on public data.</li>
                  <li>✅ A measure of consistency with organic growth patterns.</li>
                  <li>✅ A tool for risk management.</li>
                </ul>
              </div>
              <div className="bg-red-50 dark:bg-red-900/10 p-4 rounded-lg border border-red-100 dark:border-red-900/20">
                <h3 className="font-bold text-red-700 dark:text-red-400 mb-2">It is NOT:</h3>
                <ul className="list-disc list-inside text-sm text-slate-600 dark:text-slate-400 space-y-1">
                  <li>❌ A judgment of an influencer's character.</li>
                  <li>❌ A detection of "non-organic accounts".</li>
                  <li>❌ A guarantee of campaign performance.</li>
                </ul>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4 text-primary">How It Works</h2>
            <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-6">
              Our system analyzes public interactions using three independent layers:
            </p>
            
            <div className="space-y-6">
              <div className="border-l-4 border-primary pl-4">
                <h3 className="text-lg font-bold">1. Heuristics (The Math)</h3>
                <p className="text-slate-600 dark:text-slate-400 mt-1">
                  Measures raw engagement rates, comment entropy (variety), and timing variance. 
                  <br/><span className="text-sm italic text-slate-500">Example: If 500 comments arrive in the same minute, entropy drops, lowering the signal.</span>
                </p>
              </div>

              <div className="border-l-4 border-primary pl-4">
                <h3 className="text-lg font-bold">2. Graph Intelligence (The Network)</h3>
                <p className="text-slate-600 dark:text-slate-400 mt-1">
                  Analyzes anonymous coordination patterns.
                  <br/><span className="text-sm italic text-slate-500">Example: If a group of users consistently interacts with the same cluster of creators, it may indicate a "pod" (coordinated support group).</span>
                </p>
              </div>

              <div className="border-l-4 border-primary pl-4">
                <h3 className="text-lg font-bold">3. LLM Refinement (The Context)</h3>
                <p className="text-slate-600 dark:text-slate-400 mt-1">
                  Uses advanced AI to understand slang, sarcasm, and cultural nuance.
                  <br/><span className="text-sm italic text-slate-500">Example: "I hate you (affectionate)" is recognized as positive engagement, not toxicity.</span>
                </p>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold mb-4 text-primary">Interpreting the Signal</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <th className="py-3 pr-4 font-bold">Signal Strength</th>
                    <th className="py-3 pr-4 font-bold">Interpretation</th>
                    <th className="py-3 font-bold">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  <tr>
                    <td className="py-3 font-mono text-green-500 font-bold">80 - 100</td>
                    <td className="py-3 font-bold">High Confidence</td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">Consistent with organic, high-value engagement.</td>
                  </tr>
                  <tr>
                    <td className="py-3 font-mono text-yellow-500 font-bold">60 - 79</td>
                    <td className="py-3 font-bold">Moderate Confidence</td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">Generally organic, with some statistical anomalies.</td>
                  </tr>
                  <tr>
                    <td className="py-3 font-mono text-orange-500 font-bold">40 - 59</td>
                    <td className="py-3 font-bold">Low Confidence</td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">Significant atypical patterns detected. Manual review recommended.</td>
                  </tr>
                  <tr>
                    <td className="py-3 font-mono text-red-500 font-bold">0 - 39</td>
                    <td className="py-3 font-bold">Very Low Confidence</td>
                    <td className="py-3 text-slate-600 dark:text-slate-400">Highly coordinated or atypical behavior observed.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </div>
      <Footer />
    </div>
  );
}
