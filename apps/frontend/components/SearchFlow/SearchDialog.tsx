"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { X, Instagram, Youtube, Music, Globe, CheckCircle, Clock, AlertTriangle } from 'lucide-react';
import ObservationLoader from './ObservationLoader';
import ThresholdScreen from './ThresholdScreen';

interface SearchDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

interface Platform {
  id: string;
  name: string;
  icon: React.ReactNode;
  color: string;
  placeholder: string;
}

const platforms: Platform[] = [
  {
    id: 'instagram',
    name: 'Instagram',
    icon: <Instagram className="w-4 h-4" />,
    color: 'bg-pink-500',
    placeholder: '@username or instagram.com/username'
  },
  {
    id: 'tiktok',
    name: 'TikTok',
    icon: <Music className="w-4 h-4" />,
    color: 'bg-black',
    placeholder: '@username or tiktok.com/@username'
  },
  {
    id: 'youtube',
    name: 'YouTube',
    icon: <Youtube className="w-4 h-4" />,
    color: 'bg-red-500',
    placeholder: 'channel name or youtube.com/@username'
  },
  {
    id: 'other',
    name: 'Other',
    icon: <Globe className="w-4 h-4" />,
    color: 'bg-gray-500',
    placeholder: 'Enter profile handle or URL'
  }
];

export default function SearchDialog({ isOpen, onClose }: SearchDialogProps) {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [handle, setHandle] = useState('');
  const [detectedPlatform, setDetectedPlatform] = useState<Platform | null>(null);
  const [acknowledgments, setAcknowledgments] = useState({
    probabilistic: false,
    incomplete: false,
    variable: false
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showLoader, setShowLoader] = useState(false);
  const [showThreshold, setShowThreshold] = useState(false);

  const detectPlatform = (input: string): Platform | null => {
    const instagram = /(?:@|(?:instagram\.com\/))([a-zA-Z0-9_.]+)/;
    const tiktok = /(?:@|(?:tiktok\.com\/[@]?))([a-zA-Z0-9_.]+)/;
    const youtube = /(?:@|(?:youtube\.com\/[@]))([a-zA-Z0-9_.]+)/;

    if (instagram.test(input)) return platforms.find(p => p.id === 'instagram') || null;
    if (tiktok.test(input)) return platforms.find(p => p.id === 'tiktok') || null;
    if (youtube.test(input)) return platforms.find(p => p.id === 'youtube') || null;
    
    return null;
  };

  const handleHandleChange = (input: string) => {
    setHandle(input);
    const platform = detectPlatform(input);
    setDetectedPlatform(platform);
  };

  const canProceedToStep2 = () => {
    return handle.trim() && detectedPlatform;
  };

  const canProceedToStep3 = () => {
    return true; // Step 2 is pre-selected and non-editable for MVP
  };

  const canSubmit = () => {
    return acknowledgments.probabilistic && acknowledgments.incomplete && acknowledgments.variable;
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Close dialog and show loader
    onClose();
    setShowLoader(true);
  };

  const handleLoaderComplete = () => {
    setShowLoader(false);
    setShowThreshold(true);
  };

  const handleViewReport = () => {
    const cleanHandle = handle.replace(/[@\/]/g, '').trim();
    setShowThreshold(false);
    router.push(`/report/${cleanHandle}`);
  };

  const resetAndClose = () => {
    setCurrentStep(1);
    setHandle('');
    setDetectedPlatform(null);
    setAcknowledgments({ probabilistic: false, incomplete: false, variable: false });
    setIsSubmitting(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-slate-900 rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <div>
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
              Submit Analysis Request
            </h2>
            <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
              I am asking the system to observe, not to judge.
            </p>
          </div>
          <button
            onClick={resetAndClose}
            className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5 text-slate-500" />
          </button>
        </div>

        {/* Progress Indicator */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center space-x-4">
            {[1, 2, 3].map((step) => (
              <div key={step} className="flex items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    currentStep >= step
                      ? 'bg-emerald-500 text-white'
                      : 'bg-slate-200 dark:bg-slate-700 text-slate-500'
                  }`}
                >
                  {step}
                </div>
                <span
                  className={`ml-2 text-sm ${
                    currentStep >= step
                      ? 'text-emerald-600 dark:text-emerald-400 font-medium'
                      : 'text-slate-500'
                  }`}
                >
                  {step === 1 && 'Identification'}
                  {step === 2 && 'Scope Declaration'}
                  {step === 3 && 'Acknowledgement'}
                </span>
                {step < 3 && <div className="w-8 h-px bg-slate-300 dark:bg-slate-600 mx-4" />}
              </div>
            ))}
          </div>
        </div>

        {/* Step 1: Identification */}
        {currentStep === 1 && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                Identify the Public Profile
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Only publicly visible activity can be observed.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Profile Handle or URL
                </label>
                <input
                  type="text"
                  value={handle}
                  onChange={(e) => handleHandleChange(e.target.value)}
                  placeholder={detectedPlatform?.placeholder || "Enter profile handle or URL"}
                  className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-colors"
                />
              </div>

              {detectedPlatform && (
                <div className="flex items-center gap-2 p-3 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
                  <div className={`p-2 rounded-lg ${detectedPlatform.color} text-white`}>
                    {detectedPlatform.icon}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900 dark:text-white">
                      Platform detected: {detectedPlatform.name}
                    </p>
                    <p className="text-xs text-slate-600 dark:text-slate-400">
                      Format validated and ready for observation
                    </p>
                  </div>
                </div>
              )}

              <div className="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5" />
                  <div className="text-xs text-amber-700 dark:text-amber-300">
                    <p className="font-medium">Private accounts cannot be observed</p>
                    <p className="text-amber-600 dark:text-amber-400">Ensure the profile is public before proceeding</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-between">
              <button
                onClick={resetAndClose}
                className="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => setCurrentStep(2)}
                disabled={!canProceedToStep2()}
                className="px-6 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-300 dark:disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
              >
                Continue to Scope Declaration
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Scope Declaration */}
        {currentStep === 2 && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                Declare Observation Scope
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Private content and deleted activity cannot be included.
              </p>
            </div>

            <div className="space-y-4">
              <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-emerald-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                        Public posts (last 12)
                      </p>
                      <p className="text-xs text-slate-600 dark:text-slate-400">
                        Recent publicly visible content
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-emerald-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                        Public engagement counts
                      </p>
                      <p className="text-xs text-slate-600 dark:text-slate-400">
                        Likes, comments, shares visible to public
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-emerald-500" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                        Public comments (if available)
                      </p>
                      <p className="text-xs text-slate-600 dark:text-slate-400">
                        Comments that are publicly accessible
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="flex items-start gap-2">
                  <Clock className="w-4 h-4 text-blue-600 dark:text-blue-400 mt-0.5" />
                  <div className="text-xs text-blue-700 dark:text-blue-300">
                    <p className="font-medium">Estimated processing time: 2-4 minutes</p>
                    <p className="text-blue-600 dark:text-blue-400">Time varies based on profile activity and platform response</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-between">
              <button
                onClick={() => setCurrentStep(1)}
                className="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
              >
                Back
              </button>
              <button
                onClick={() => setCurrentStep(3)}
                className="px-6 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg font-medium transition-colors"
              >
                Continue to Acknowledgement
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Acknowledgement */}
        {currentStep === 3 && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                Acknowledge Limitations
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Understanding these constraints is essential for proper interpretation.
              </p>
            </div>

            <div className="space-y-4">
              <label className="flex items-start gap-3 p-4 rounded-lg border border-slate-200 dark:border-slate-700 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                <input
                  type="checkbox"
                  checked={acknowledgments.probabilistic}
                  onChange={(e) => setAcknowledgments(prev => ({ ...prev, probabilistic: e.target.checked }))}
                  className="mt-1 w-4 h-4 text-emerald-500 border-slate-300 dark:border-slate-600 rounded focus:ring-emerald-500"
                />
                <div>
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                    This analysis is probabilistic, not definitive
                  </p>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                    Results represent likelihoods based on available data, not absolute certainty
                  </p>
                </div>
              </label>

              <label className="flex items-start gap-3 p-4 rounded-lg border border-slate-200 dark:border-slate-700 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                <input
                  type="checkbox"
                  checked={acknowledgments.incomplete}
                  onChange={(e) => setAcknowledgments(prev => ({ ...prev, incomplete: e.target.checked }))}
                  className="mt-1 w-4 h-4 text-emerald-500 border-slate-300 dark:border-slate-600 rounded focus:ring-emerald-500"
                />
                <div>
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                    Some data may be missing or inaccessible
                  </p>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                    Private content, deleted posts, or platform limitations may affect completeness
                  </p>
                </div>
              </label>

              <label className="flex items-start gap-3 p-4 rounded-lg border border-slate-200 dark:border-slate-700 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                <input
                  type="checkbox"
                  checked={acknowledgments.variable}
                  onChange={(e) => setAcknowledgments(prev => ({ ...prev, variable: e.target.checked }))}
                  className="mt-1 w-4 h-4 text-emerald-500 border-slate-300 dark:border-slate-600 rounded focus:ring-emerald-500"
                />
                <div>
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                    Scores may change on re-analysis
                  </p>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                    New data or updated algorithms can produce different results over time
                  </p>
                </div>
              </label>
            </div>

            <div className="p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
              <div className="flex items-start gap-2">
                <CheckCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-400 mt-0.5" />
                <div className="text-xs text-emerald-700 dark:text-emerald-300">
                  <p className="font-medium">Ready to submit request</p>
                  <p className="text-emerald-600 dark:text-emerald-400">
                    By checking all boxes, you acknowledge the observational nature of this analysis
                  </p>
                </div>
              </div>
            </div>

            <div className="flex justify-between">
              <button
                onClick={() => setCurrentStep(2)}
                className="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 transition-colors"
              >
                Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={!canSubmit() || isSubmitting}
                className="px-6 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-slate-300 dark:disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors flex items-center gap-2"
              >
                {isSubmitting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Submitting Request...
                  </>
                ) : (
                  'Submit Request for Observation'
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}