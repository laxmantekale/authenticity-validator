import React, { useState } from 'react';
import { Upload, FileText, AlertCircle } from 'lucide-react';

export const DocumentUploader = ({ onFileSelected, accept = ".pdf,.png,.jpg,.jpeg,.webp", maxSizeMB = 16 }) => {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState('');

  const handleFiles = (files) => {
    setError('');
    if (!files || files.length === 0) return;
    const file = files[0];
    const maxBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxBytes) {
      setError(`File exceeds maximum size of ${maxSizeMB} MB.`);
      return;
    }
    onFileSelected(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div className="space-y-2">
      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById('common-doc-upload-input').click()}
        className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center transition-colors cursor-pointer ${
          dragOver ? 'border-emerald-600 bg-emerald-50/50' : 'border-slate-300 hover:border-emerald-500 bg-slate-50'
        }`}
      >
        <input
          id="common-doc-upload-input"
          type="file"
          accept={accept}
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-3">
          <Upload className="w-7 h-7" />
        </div>
        <h3 className="text-sm font-bold text-slate-900">
          Drag & drop document here, or <span className="text-emerald-600">Browse</span>
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Supported formats: PDF, PNG, JPG, or WEBP up to {maxSizeMB} MB
        </p>
      </div>
    </div>
  );
};

export default DocumentUploader;
