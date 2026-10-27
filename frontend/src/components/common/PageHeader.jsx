import React from 'react';

export const PageHeader = ({ title, subtitle, badge, action, children }) => {
  return (
    <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-5 border-b border-slate-200/80">
      <div>
        <div className="flex items-center gap-2.5 flex-wrap">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">{title}</h1>
          {badge && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
              {badge}
            </span>
          )}
        </div>
        {subtitle && <p className="text-xs sm:text-sm text-slate-500 mt-1 leading-relaxed">{subtitle}</p>}
      </div>
      {(action || children) && (
        <div className="flex items-center gap-3 shrink-0 flex-wrap">
          {action}
          {children}
        </div>
      )}
    </div>
  );
};

export default PageHeader;
