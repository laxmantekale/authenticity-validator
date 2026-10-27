import React from 'react';
import { Award, Printer, Download, Calendar } from 'lucide-react';
import StatusBadge from '../common/StatusBadge';

export const ReportCard = ({ report: rep, onView, onDownload }) => {
  const reportId = rep.report_id || rep.report_id_code;
  const docDisplayName = rep.display_name || rep.document_name || rep.document_type || 'Academic Document';

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-4 sm:p-5 shadow-sm hover:border-slate-300 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div className="flex items-start sm:items-center gap-3.5">
        <div className="w-11 h-11 rounded-xl bg-emerald-50 text-emerald-700 font-bold flex items-center justify-center shrink-0 border border-emerald-200">
          <Award className="w-5 h-5 text-emerald-600" />
        </div>

        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-sm sm:text-base font-bold text-slate-900">{docDisplayName}</h3>
            <StatusBadge status={rep.overall_status || rep.authentication_status} size="sm" />
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
            <span className="font-mono text-[11px] font-bold px-2 py-0.5 bg-slate-100 text-slate-700 rounded-md border border-slate-200">
              Verification ID: {reportId}
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              Verified: {rep.generated_at ? new Date(rep.generated_at).toLocaleDateString() : '—'}
            </span>
            <span className="text-slate-400 font-mono text-[11px]">
              Type: {rep.document_type || 'Academic'}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2 self-stretch md:self-auto">
        {onView && (
          <button
            onClick={() => onView(reportId)}
            className="flex-1 md:flex-none inline-flex items-center justify-center gap-1.5 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl text-xs sm:text-sm transition-colors shadow-sm"
          >
            <Printer className="w-4 h-4 text-emerald-400" />
            <span>View / Print Report</span>
          </button>
        )}

        {onDownload && (
          <button
            onClick={() => onDownload(reportId)}
            className="inline-flex items-center justify-center gap-1 px-3 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl text-xs sm:text-sm transition-colors"
            title="Download PDF report"
          >
            <Download className="w-4 h-4" />
            <span className="hidden sm:inline">PDF</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default ReportCard;
