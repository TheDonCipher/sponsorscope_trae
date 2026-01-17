import React from 'react';

export type WarningType = 'blocked' | 'sparse' | 'system' | 'private';

interface WarningBannerProps {
  type: WarningType;
  title?: string;
  message?: string;
}

export const WarningBanner: React.FC<WarningBannerProps> = ({ type, title, message }) => {
  const config = {
    blocked: {
      color: 'border-yellow-500 bg-yellow-900/10 text-yellow-200',
      icon: 'comments_disabled',
      defaultTitle: 'SIGNAL BLOCKED',
      defaultMessage: 'The creator has disabled comments. Linguistic analysis is unavailable.'
    },
    sparse: {
      color: 'border-slate-500 bg-slate-800/50 text-slate-300',
      icon: 'data_usage',
      defaultTitle: 'LOW SAMPLE SIZE',
      defaultMessage: 'Data points insufficient for high-confidence analysis.'
    },
    system: {
      color: 'border-purple-500 bg-purple-900/20 text-purple-200',
      icon: 'hourglass_empty',
      defaultTitle: 'SCAN PAUSED',
      defaultMessage: 'System throttling active to respect platform limits.'
    },
    private: {
      color: 'border-slate-600 bg-black/40 text-slate-400',
      icon: 'lock',
      defaultTitle: 'ACCESS DENIED',
      defaultMessage: 'This account is private. Public analysis is impossible.'
    }
  };

  const style = config[type];

  return (
    <div className={`w-full p-4 border-l-4 ${style.color} mb-6 rounded-r-lg`}>
      <div className="flex items-start gap-3">
        <span className="material-symbols-outlined opacity-80">{style.icon}</span>
        <div>
          <h4 className="font-bold text-xs uppercase tracking-wider opacity-90">
            {title || style.defaultTitle}
          </h4>
          <p className="text-sm mt-1 opacity-80 font-mono">
            {message || style.defaultMessage}
          </p>
        </div>
      </div>
    </div>
  );
};
