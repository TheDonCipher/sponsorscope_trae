"use client";

import React from 'react';
import { AlertCircle, Lock, Clock, Mail } from 'lucide-react';

interface PlatformResistanceMessageProps {
  error: {
    type: string;
    message: string;
    details?: {
      halt_reason?: string;
      halt_timestamp?: string;
      scraper_guidance?: string;
      contact_info?: string;
      client_ip?: string;
    };
    user_facing_message?: string;
    data_integrity_verdict?: string;
  };
  onRetry?: () => void;
  onContactSupport?: () => void;
}

export const PlatformResistanceMessage: React.FC<PlatformResistanceMessageProps> = ({
  error,
  onRetry,
  onContactSupport
}) => {
  const getMessageType = () => {
    switch (error.type) {
      case 'platform_resistance':
        return {
          icon: <Lock className="w-6 h-6 text-red-500" />,
          title: 'Access Restricted',
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          textColor: 'text-red-800'
        };
      case 'rate_limit':
        return {
          icon: <Clock className="w-6 h-6 text-yellow-500" />,
          title: 'Rate Limit Exceeded',
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          textColor: 'text-yellow-800'
        };
      case 'abuse_detection':
        return {
          icon: <AlertCircle className="w-6 h-6 text-orange-500" />,
          title: 'Request Blocked',
          bgColor: 'bg-orange-50',
          borderColor: 'border-orange-200',
          textColor: 'text-orange-800'
        };
      default:
        return {
          icon: <AlertCircle className="w-6 h-6 text-gray-500" />,
          title: 'Access Issue',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-200',
          textColor: 'text-gray-800'
        };
    }
  };

  const messageType = getMessageType();
  const displayMessage = error.user_facing_message || error.message;

  return (
    <div className={`${messageType.bgColor} ${messageType.borderColor} border rounded-lg p-6 max-w-2xl mx-auto my-8`}>
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          {messageType.icon}
        </div>
        
        <div className="flex-1">
          <h3 className={`text-lg font-semibold ${messageType.textColor} mb-2`}>
            {messageType.title}
          </h3>
          
          <p className={`${messageType.textColor} mb-4`}>
            {displayMessage}
          </p>

          {error.data_integrity_verdict && (
            <div className="bg-white bg-opacity-50 rounded-md p-3 mb-4">
              <p className="text-sm font-medium text-gray-700 mb-1">Data Integrity Status:</p>
              <p className="text-sm text-gray-600">{error.data_integrity_verdict}</p>
            </div>
          )}

          {error.details && (
            <div className="bg-white bg-opacity-50 rounded-md p-3 mb-4">
              <details className="text-sm">
                <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
                  Technical Details
                </summary>
                <div className="mt-2 space-y-2">
                  {error.details.halt_reason && (
                    <p><span className="font-medium">Reason:</span> {error.details.halt_reason}</p>
                  )}
                  {error.details.halt_timestamp && (
                    <p><span className="font-medium">Timestamp:</span> {new Date(error.details.halt_timestamp).toLocaleString()}</p>
                  )}
                  {error.details.client_ip && (
                    <p><span className="font-medium">Client IP:</span> {error.details.client_ip}</p>
                  )}
                  {error.details.scraper_guidance && (
                    <p><span className="font-medium">Guidance:</span> {error.details.scraper_guidance}</p>
                  )}
                </div>
              </details>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3">
            {onRetry && (
              <button
                onClick={onRetry}
                className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Try Again
              </button>
            )}
            
            {(onContactSupport || error.details?.contact_info) && (
              <button
                onClick={onContactSupport || (() => {
                  if (error.details?.contact_info) {
                    window.location.href = `mailto:${error.details.contact_info}`;
                  }
                })}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <Mail className="w-4 h-4 mr-2" />
                Contact Support
              </button>
            )}
          </div>

          <div className="mt-4 text-xs text-gray-500">
            <p>If you believe this is an error, please contact our support team with the details above.</p>
            {error.details?.contact_info && (
              <p className="mt-1">
                Support: <a href={`mailto:${error.details.contact_info}`} className="text-indigo-600 hover:text-indigo-500">
                  {error.details.contact_info}
                </a>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlatformResistanceMessage;