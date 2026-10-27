import React from 'react';
import { FileText, Eye, Trash2 } from 'lucide-react';
import StatusBadge from '../common/StatusBadge';

export const DocumentCard = ({ document: doc, onView, onDelete }) => {
  const docDisplayName = doc.display_name || doc.name || doc.document_type || 'Academic Document';

  return (
    <div className="p-4 bg-white rounded-2xl border border-slate-200 shadow-sm hover:border-slate-300 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div className="flex items-start sm:items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0 border border-emerald-100">
          <FileText className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-xs sm:text-sm font-bold text-slate-900">{docDisplayName}</h4>
          <p className="text-[11px] text-slate-500 font-mono">
            {doc.document_type} {doc.uploaded_at && `• ${new Date(doc.uploaded_at).toLocaleDateString()}`}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 self-start sm:self-center">
        <StatusBadge status={doc.verification_status || doc.latest_status || 'Not Verified'} size="sm" />
        {onView && (
          <button
            onClick={() => onView(doc)}
            className="inline-flex items-center gap-1 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-colors"
          >
            <Eye className="w-3.5 h-3.5" />
            <span>View</span>
          </button>
        )}
        {onDelete && (
          <button
            onClick={() => onDelete(doc)}
            className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default DocumentCard;
