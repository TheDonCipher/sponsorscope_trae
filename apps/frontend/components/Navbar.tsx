import Link from 'next/link';

export const Navbar = () => {
  return (
    <nav className="sticky top-0 z-50 border-b border-border-light dark:border-border-dark bg-surface-light/90 dark:bg-surface-dark/90 backdrop-blur-md">
      <div className="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <div className="flex items-center justify-center size-8 rounded bg-primary/10 text-primary">
              <span className="material-symbols-outlined text-xl">analytics</span>
            </div>
            <span className="text-lg font-bold tracking-tight text-[#101816] dark:text-white">SponsorScope.ai</span>
          </Link>
          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            <Link className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors" href="/methodology">Methodology</Link>
            <Link className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors" href="/pricing">Pricing</Link>
            <Link className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors" href="/docs">API Docs</Link>
          </div>
          {/* Action */}
          <div className="flex items-center gap-4">
            <Link className="text-sm font-medium text-slate-600 dark:text-slate-300 hidden sm:block" href="/login">Login</Link>
            <button className="flex items-center justify-center h-9 px-4 rounded-lg bg-primary hover:bg-emerald-400 text-[#101816] text-sm font-bold transition-all shadow-sm shadow-primary/20">
              Get Started
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};
