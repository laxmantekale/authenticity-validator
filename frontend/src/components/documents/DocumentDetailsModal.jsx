import React, { useState } from 'react';
import { Modal } from '../common/Modal';
import StatusBadge from '../common/StatusBadge';
import { FileText, Download, ShieldCheck, Eye, AlertCircle, Clock, Hash, Calendar } from 'lucide-react';

export const DocumentDetailsModal = ({ isOpen, onClose, document: doc, onVerify }) => {
  const [previewError, setPreviewError] = useState(false);

  if (!doc) return null;

  const title = doc.original_filename || doc.document_title || doc.document_type || 'Academic Document';
  const fileExt = (doc.original_filename || '').split('.').pop().toLowerCase();
  const isPdf = fileExt === 'pdf' || (doc.mime_type && doc.mime_type.includes('pdf'));
  const isImage = ['png', 'jpg', 'jpeg', 'webp'].includes(fileExt) || (doc.mime_type && doc.mime_type.startsWith('image/'));

  const viewUrl = `/api/documents/${doc.id}/view`;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Document Details & Preview" maxWidth="max-w-2xl">
      <div className="space-y-6">
        
        {/* Document Header Info */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center shrink-0">
              <FileText className="w-5 h-5" />
            </div>
            <div className="min-w-0">
              <h4 className="text-sm font-bold text-slate-900 truncate">{title}</h4>
              <p className="text-xs text-slate-500">{doc.document_type || 'Academic Certificate'}</p>
            </div>
          </div>
          <div className="self-start sm:self-center">
            <StatusBadge status={doc.verification_status || 'PENDING'} />
          </div>
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="p-3 bg-white rounded-lg border border-slate-200 flex items-center gap-2.5">
            <Hash className="w-4 h-4 text-slate-400 shrink-0" />
            <div className="min-w-0">
              <span className="text-slate-500 block text-[11px]">Verification Code</span>
              <span className="font-mono font-semibold text-slate-800 truncate block">
                {doc.verification_code || `DOC-${doc.id}`}
              </span>
            </div>
          </div>

          <div className="p-3 bg-white rounded-lg border border-slate-200 flex items-center gap-2.5">
            <Calendar className="w-4 h-4 text-slate-400 shrink-0" />
            <div className="min-w-0">
              <span className="text-slate-500 block text-[11px]">Uploaded Date</span>
              <span className="font-semibold text-slate-800 truncate block">
                {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleString() : 'N/A'}
              </span>
            </div>
          </div>

          {doc.file_size_formatted && (
            <div className="p-3 bg-white rounded-lg border border-slate-200 flex items-center gap-2.5">
              <FileText className="w-4 h-4 text-slate-400 shrink-0" />
              <div className="min-w-0">
                <span className="text-slate-500 block text-[11px]">File Size</span>
                <span className="font-semibold text-slate-800">{doc.file_size_formatted}</span>
              </div>
            </div>
          )}

          {doc.page_count && (
            <div className="p-3 bg-white rounded-lg border border-slate-200 flex items-center gap-2.5">
              <Eye className="w-4 h-4 text-slate-400 shrink-0" />
              <div className="min-w-0">
                <span className="text-slate-500 block text-[11px]">Pages</span>
                <span className="font-semibold text-slate-800">{doc.page_count} page(s)</span>
              </div>
            </div>
          )}
        </div>

        {/* File Preview Container */}
        <div className="border border-slate-200 rounded-xl overflow-hidden bg-slate-50/50">
          <div className="p-2.5 bg-slate-100 border-b border-slate-200 flex items-center justify-between text-xs text-slate-600">
            <span className="font-semibold">Document Preview</span>
            <a
              href={viewUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center gap-1 text-[11px]"
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Open in New Tab</span>
            </a>
          </div>

          <div className="p-4 flex items-center justify-center min-h-[260px] max-h-[380px] overflow-auto">
            {previewError ? (
              <div className="text-center py-6 text-slate-500 space-y-2">
                <AlertCircle className="w-10 h-10 text-amber-500 mx-auto" />
                <p className="text-xs font-semibold">Preview not available in this frame.</p>
                <p className="text-[11px] text-slate-400">You can still open or download the file directly.</p>
              </div>
            ) : isImage ? (
              <img
                src={viewUrl}
                alt="Document Preview"
                onError={() => setPreviewError(true)}
                className="max-h-[340px] max-w-full object-contain rounded border border-slate-200 shadow-xs"
              />
            ) : isPdf ? (
              <iframe
                src={`${viewUrl}#toolbar=0`}
                title="PDF Preview"
                onError={() => setPreviewError(true)}
                className="w-full h-[320px] rounded border border-slate-200 bg-white"
              />
            ) : (
              <div className="text-center py-8 text-slate-500 space-y-2">
                <FileText className="w-12 h-12 text-slate-400 mx-auto" />
                <p className="text-xs font-semibold text-slate-700">{title}</p>
                <p className="text-[11px] text-slate-400">File ready for validation pipeline</p>
              </div>
            )}
          </div>
        </div>

        {/* Modal Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-100">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-700 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
          >
            Close
          </button>
          
          <a
            href={viewUrl}
            target="_blank"
            rel="noopener noreferrer"
            download={doc.original_filename || 'document'}
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold rounded-lg transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download</span>
          </a>

          {onVerify && (
            <button
              type="button"
              onClick={() => {
                onClose();
                onVerify(doc);
              }}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors cursor-pointer"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Verify Document</span>
            </button>
          )}
        </div>

      </div>
    </Modal>
  );
};

export default DocumentDetailsModal;
