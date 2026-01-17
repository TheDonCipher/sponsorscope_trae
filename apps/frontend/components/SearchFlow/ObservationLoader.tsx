"use client";

import { useState, useEffect } from 'react';
import { CheckCircle, Clock, Circle } from 'lucide-react';

interface ObservationLoaderProps {
  isVisible: boolean;
  onComplete: () => void;
}

interface StatusEntry {
  id: string;
  text: string;
  status: 'completed' | 'in_progress' | 'pending';
  timestamp?: string;
}

export default function ObservationLoader({ isVisible, onComplete }: ObservationLoaderProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [statusEntries, setStatusEntries] = useState<StatusEntry[]>([
    { id: '1', text: 'Request received', status: 'completed', timestamp: 'Just now' },
    { id: '2', text: 'Collecting public activity', status: 'in_progress' },
    { id: '3', text: 'Assessing engagement consistency', status: 'pending' },
    { id: '4', text: 'Calibrating uncertainty', status: 'pending' },
    { id: '5', text: 'Observation complete', status: 'pending' }
  ]);

  const [constraints, setConstraints] = useState<string[]>([]);

  useEffect(() => {
    if (!isVisible) return;

    const timers = [
      // Step 1: Collecting public activity
      setTimeout(() => {
        setStatusEntries(prev => prev.map(entry => 
          entry.id === '2' 
            ? { ...entry, status: 'completed' as const, timestamp: '30s ago' }
            : entry
        ));
        setCurrentStep(1);
        
        // Simulate detecting constraints
        if (Math.random() > 0.7) {
          setConstraints(prev => [...prev, "Comments appear to be limited on this profile"]);
        }
      }, 2000),

      // Step 2: Assessing engagement consistency
      setTimeout(() => {
        setStatusEntries(prev => prev.map(entry => 
          entry.id === '3' 
            ? { ...entry, status: 'in_progress' as const }
            : entry
        ));
        setCurrentStep(2);
      }, 4000),

      setTimeout(() => {
        setStatusEntries(prev => prev.map(entry => 
          entry.id === '3' 
            ? { ...entry, status: 'completed' as const, timestamp: '1m ago' }
            : entry
        ));
        setCurrentStep(3);
      }, 6000),

      // Step 3: Calibrating uncertainty
      setTimeout(() => {
        setStatusEntries(prev => prev.map(entry => 
          entry.id === '4' 
            ? { ...entry, status: 'in_progress' as const }
            : entry
        ));
        setCurrentStep(4);
      }, 8000),

      setTimeout(() => {
        setStatusEntries(prev => prev.map(entry => 
          entry.id === '4' 
            ? { ...entry, status: 'completed' as const, timestamp: '2m ago' }
            : entry
        ));
        setCurrentStep(5);
      }, 10000),

      // Final step: Observation complete
      setTimeout(() => {
        setStatusEntries(prev => prev.map(entry => 
          entry.id === '5' 
            ? { ...entry, status: 'completed' as const, timestamp: 'Just now' }
            : entry
        ));
        setCurrentStep(6);
        
        // Call completion callback after a short delay
        setTimeout(() => {
          onComplete();
        }, 1500);
      }, 12000)
    ];

    return () => {
      timers.forEach(timer => clearTimeout(timer));
    };
  }, [isVisible, onComplete]);

  if (!isVisible) return null;

  const getStatusIcon = (status: StatusEntry['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'in_progress':
        return <Clock className="w-4 h-4 text-blue-500 animate-pulse" />;
      case 'pending':
        return <Circle className="w-4 h-4 text-slate-400" />;
    }
  };

  const getStatusTextClass = (status: StatusEntry['status']) => {
    switch (status) {
      case 'completed':
        return 'text-emerald-700 dark:text-emerald-300';
      case 'in_progress':
        return 'text-blue-700 dark:text-blue-300 font-medium';
      case 'pending':
        return 'text-slate-500 dark:text-slate-400';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-slate-900 rounded-lg shadow-xl max-w-2xl w-full mx-4 p-8">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-2">
            Observation in Progress
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Your request has been recorded. Observation is in progress.
          </p>
        </div>

        {/* Status Ledger */}
        <div className="space-y-4 mb-6">
          {statusEntries.map((entry, index) => (
            <div key={entry.id} className="flex items-center gap-4 p-4 rounded-lg border border-slate-200 dark:border-slate-700">
              <div className="flex-shrink-0">
                {getStatusIcon(entry.status)}
              </div>
              <div className="flex-1">
                <p className={`text-sm ${getStatusTextClass(entry.status)}`}>
                  {entry.text}
                </p>
                {entry.timestamp && (
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    {entry.timestamp}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Early Constraint Disclosure */}
        {constraints.length > 0 && (
          <div className="mb-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
            <div className="flex items-start gap-2">
              <div className="w-4 h-4 bg-amber-500 rounded-full flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-amber-800 dark:text-amber-200">
                  Observed constraints that may affect confidence:
                </p>
                <ul className="text-xs text-amber-700 dark:text-amber-300 mt-1 space-y-1">
                  {constraints.map((constraint, index) => (
                    <li key={index}>• {constraint}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mb-2">
            <span>Processing request</span>
            <span>{currentStep}/6 steps completed</span>
          </div>
          <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
            <div 
              className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${(currentStep / 6) * 100}%` }}
            />
          </div>
        </div>

        <div className="text-center">
          <p className="text-xs text-slate-500 dark:text-slate-400">
            This process typically takes 2-4 minutes. Please remain on this page.
          </p>
        </div>
      </div>
    </div>
  );
}