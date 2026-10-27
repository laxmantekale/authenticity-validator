import React from 'react';

export const StatCard = ({ title, value, icon: Icon, color = 'blue', change, changeType = 'neutral', subtitle }) => {
  const colorSchemes = {
    blue: { iconBg: 'bg-blue-50 text-blue-600 border-blue-100' },
    emerald: { iconBg: 'bg-emerald-50 text-emerald-600 border-emerald-100' },
    amber: { iconBg: 'bg-amber-50 text-amber-600 border-amber-100' },
    rose: { iconBg: 'bg-rose-50 text-rose-600 border-rose-100' },
    slate: { iconBg: 'bg-slate-100 text-slate-700 border-slate-200' },
    indigo: { iconBg: 'bg-indigo-50 text-indigo-600 border-indigo-100' }
  };

  const scheme = colorSchemes[color] || colorSchemes.blue;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-shadow relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</p>
          <p className="text-2xl font-bold text-slate-900 mt-1.5">{value}</p>
          {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl border ${scheme.iconBg}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      {change !== undefined && (
        <div className="mt-3 pt-3 border-t border-slate-100 flex items-center text-xs">
          <span className={`font-medium ${changeType === 'positive' ? 'text-emerald-600' : changeType === 'negative' ? 'text-rose-600' : 'text-slate-500'}`}>
            {change}
          </span>
        </div>
      )}
    </div>
  );
};

export default StatCard;
