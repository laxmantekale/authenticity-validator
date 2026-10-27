import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const ErrorState = ({
  title = 'Unable to load information',
  message = 'An error occurred while communicating with the service. Please try again.',
  onRetry
}) => {
  return (
    <div className="bg-rose-50/60 rounded-xl border border-rose-200 p-6 sm:p-8 text-center max-w-lg mx-auto my-6">
      <div className="w-10 h-10 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto mb-3">
        <AlertCircle className="w-5 h-5" />
      </div>
      <h3 className="text-sm font-bold text-rose-900 mb-1">{title}</h3>
      <p className="text-xs text-rose-700 max-w-sm mx-auto leading-relaxed mb-5">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-white border border-rose-300 text-rose-800 text-xs font-semibold hover:bg-rose-100/50 transition-colors shadow-xs cursor-pointer"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry</span>
        </button>
      )}
    </div>
  );
};

export default ErrorState;
