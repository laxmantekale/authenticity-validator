import React from 'react';
import { FileText } from 'lucide-react';

export const DocumentPreview = ({ file, filePreview }) => {
  if (!file) return null;

  return (
    <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex flex-col items-center justify-center min-h-48">
      {filePreview ? (
        <img
          src={filePreview}
          alt="Document Preview"
          className="max-h-64 object-contain rounded-lg shadow-sm border border-slate-200"
        />
      ) : (
        <div className="text-center py-6">
          <FileText className="w-16 h-16 text-emerald-600 mx-auto mb-2 opacity-80" />
          <p className="text-xs font-semibold text-slate-700">PDF Document Ready for OCR & Tamper Analysis</p>
          <p className="text-[11px] text-slate-400 mt-0.5">{file.name}</p>
        </div>
      )}
    </div>
  );
};

export default DocumentPreview;
