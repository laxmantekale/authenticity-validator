import React from 'react';
import { CheckCircle2, AlertCircle, AlertTriangle, Info, X } from 'lucide-react';

export const ToastItem = ({ toast, onClose }) => {
  const { id, type = 'info', title, message } = toast;

  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />,
    error: <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />,
    warning: <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0" />,
    info: <Info className="w-5 h-5 text-blue-600 shrink-0" />
  };

  const borderLeft = {
    success: 'border-l-4 border-l-emerald-500',
    error: 'border-l-4 border-l-rose-500',
    warning: 'border-l-4 border-l-amber-500',
    info: 'border-l-4 border-l-blue-500'
  };

  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-xl border border-slate-200 bg-white shadow-lg ${borderLeft[type] || borderLeft.info} transition-all duration-300 max-w-md w-full pointer-events-auto`}
      role="alert"
    >
      <div className="mt-0.5">{icons[type] || icons.info}</div>
      <div className="flex-1 min-w-0">
        {title && <h4 className="text-sm font-semibold text-slate-900 leading-tight">{title}</h4>}
        <p className="text-xs text-slate-600 mt-0.5 leading-relaxed break-words">{message}</p>
      </div>
      <button
        onClick={() => onClose(id)}
        className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors"
        aria-label="Close notification"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};

export const ToastContainer = ({ toasts, removeToast }) => {
  return (
    <div className="fixed top-5 right-5 z-[9999] flex flex-col gap-2 pointer-events-none max-w-sm w-full px-4 sm:px-0">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onClose={removeToast} />
      ))}
    </div>
  );
};

export default ToastItem;
