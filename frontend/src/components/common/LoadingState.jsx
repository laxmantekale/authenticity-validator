import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingState = ({ message = 'Loading details...' }) => {
  return (
    <div className="py-12 flex flex-col items-center justify-center text-center">
      <Loader2 className="w-8 h-8 text-slate-700 animate-spin mb-3" />
      <p className="text-xs font-medium text-slate-500">{message}</p>
    </div>
  );
};

export const TableSkeleton = ({ rows = 5, cols = 4 }) => {
  return (
    <div className="animate-pulse space-y-3 p-4">
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="flex gap-4">
          {Array.from({ length: cols }).map((_, c) => (
            <div key={c} className="h-4 bg-slate-200 rounded flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
};

export default LoadingState;
