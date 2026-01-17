import { Footer } from '../../components/Footer';

export default function ApiDocs() {
  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark text-[#101816] dark:text-white font-display">
      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 border-r border-border-light dark:border-border-dark min-h-[calc(100vh-64px)] hidden md:block p-6">
          <h3 className="font-bold text-sm uppercase tracking-wider text-slate-500 mb-4">Core Resources</h3>
          <ul className="space-y-3 text-sm">
            <li><a href="#" className="text-primary font-medium">Introduction</a></li>
            <li><a href="#" className="text-slate-600 dark:text-slate-400 hover:text-primary">Authentication</a></li>
            <li><a href="#" className="text-slate-600 dark:text-slate-400 hover:text-primary">Rate Limits</a></li>
          </ul>
          <h3 className="font-bold text-sm uppercase tracking-wider text-slate-500 mt-8 mb-4">Endpoints</h3>
          <ul className="space-y-3 text-sm">
            <li><a href="#" className="text-slate-600 dark:text-slate-400 hover:text-primary">GET /report/{'{handle}'}</a></li>
            <li><a href="#" className="text-slate-600 dark:text-slate-400 hover:text-primary">GET /evidence/{'{id}'}</a></li>
          </ul>
        </div>

        {/* Content */}
        <div className="flex-1 p-8 md:p-12 max-w-4xl">
          <div className="prose dark:prose-invert max-w-none">
            <h1>API Documentation</h1>
            <p className="lead">
              Integrate SponsorScope's vetting intelligence directly into your CRM or influencer marketing platform.
            </p>

            <hr className="my-8 border-border-light dark:border-border-dark" />

            <h2>Introduction</h2>
            <p>
              The SponsorScope API is organized around REST. Our API has predictable resource-oriented URLs, accepts form-encoded request bodies, returns JSON-encoded responses, and uses standard HTTP response codes, authentication, and verbs.
            </p>

            <h3>Base URL</h3>
            <div className="bg-slate-900 text-slate-200 p-4 rounded-lg font-mono text-sm mb-6">
              https://api.sponsorscope.ai/v1
            </div>

            <h2>Authentication</h2>
            <p>
              Authenticate your account when using the API by including your secret API key in the request. You can manage your API keys in the Dashboard.
            </p>
            <div className="bg-slate-900 text-slate-200 p-4 rounded-lg font-mono text-sm mb-6">
              Authorization: Bearer YOUR_API_KEY
            </div>

            <h2>Get Report</h2>
            <p>
              Retrieves the full analysis report for a specific social media handle. If the report does not exist, it will trigger a new scan (which may take up to 30 seconds).
            </p>

            <div className="bg-slate-100 dark:bg-slate-800/50 p-4 rounded-lg border border-slate-200 dark:border-slate-700 mb-4">
              <span className="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-bold mr-2">GET</span>
              <span className="font-mono text-sm">/report/{'{handle}'}</span>
            </div>

            <h4>Response</h4>
            <pre className="bg-slate-900 text-slate-200 p-4 rounded-lg font-mono text-xs overflow-x-auto">
{`{
  "id": "rep_123456789",
  "handle": "tech_guru",
  "platform": "instagram",
  "generated_at": "2024-03-15T10:30:00Z",
  "data_completeness": "full",
  "true_engagement": {
    "signal_strength": 85.4,
    "confidence": 0.92,
    "flags": []
  },
  "audience_authenticity": {
    "signal_strength": 92.1,
    "confidence": 0.88,
    "flags": []
  }
}`}
            </pre>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}
