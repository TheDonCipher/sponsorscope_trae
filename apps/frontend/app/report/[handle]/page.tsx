"use client";
import { ReportView } from '../../../components/ReportView/ReportView';
import { useParams } from 'next/navigation';

export default function ReportPage() {
  const params = useParams();
  const handle = params?.handle as string;
  
  if (!handle) return null;

  return (
    <div className="min-h-screen bg-background-light dark:bg-background-dark font-display">
       <nav className="sticky top-0 z-50 bg-white/90 dark:bg-[#1b212d]/90 backdrop-blur-md border-b border-[#f0f5f3] dark:border-gray-800">
        <div className="px-4 md:px-10 py-3 max-w-7xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-[#101816] dark:text-white min-w-fit cursor-pointer" onClick={() => window.location.href = '/'}>
            <div className="size-8 bg-primary rounded-lg flex items-center justify-center text-white">
              <span className="material-symbols-outlined text-[20px]">radar</span>
            </div>
            <h2 className="text-xl font-bold tracking-tight">SponsorScope</h2>
          </div>
           <div className="flex items-center gap-4 md:gap-6">
              <a href="/" className="text-sm font-bold text-slate-600 hover:text-primary">Back to Search</a>
           </div>
        </div>
      </nav>
      <ReportView handle={handle} />
    </div>
  );
}
