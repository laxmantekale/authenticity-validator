import React from 'react';
import { Cpu } from 'lucide-react';

export const VerificationProgress = ({ currentStepIndex, steps }) => {
  const percent = steps.length > 0 ? Math.round(((currentStepIndex + 1) / steps.length) * 100) : 0;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-8 sm:p-12 shadow-sm text-center space-y-6">
      <div className="relative w-20 h-20 mx-auto">
        <div className="absolute inset-0 rounded-full border-4 border-emerald-100" />
        <div className="absolute inset-0 rounded-full border-4 border-emerald-600 border-t-transparent animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center text-emerald-600">
          <Cpu className="w-8 h-8 animate-pulse" />
        </div>
      </div>

      <div>
        <h2 className="text-xl font-bold text-slate-900">Running Multi-Signal Verification</h2>
        <p className="text-xs text-slate-500 mt-1">
          Evaluating document authenticity with OCR, multi-signal verification checks, and blockchain anchoring...
        </p>
      </div>

      <div className="max-w-md mx-auto p-4 bg-slate-900 text-white rounded-xl shadow-inner font-mono text-xs text-left space-y-2">
        <div className="flex items-center justify-between text-[11px] text-emerald-400 font-bold border-b border-slate-800 pb-1.5">
          <span>ACTIVE VERIFICATION ENGINE</span>
          <span>{percent}%</span>
        </div>
        <p className="text-emerald-300 animate-pulse font-semibold">
          &gt; {steps[currentStepIndex] || 'Running checks...'}
        </p>
      </div>
    </div>
  );
};

export default VerificationProgress;
