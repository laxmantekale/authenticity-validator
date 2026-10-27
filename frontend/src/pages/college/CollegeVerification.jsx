import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  ShieldCheck,
  Loader2,
  ArrowRight,
  User,
  Sparkles
} from 'lucide-react';
import { collegeService } from '../../services/collegeService';
import { reportService } from '../../services/reportService';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import VerificationResult from '../../components/verification/VerificationResult';

export const CollegeVerification = () => {
  const { toast } = useToast();
  const fileInputRef = useRef(null);

  const [file, setFile] = useState(null);
  const [candidateName, setCandidateName] = useState('');
  const [dragOver, setDragOver] = useState(false);

  // Verification state
  const [isVerifying, setIsVerifying] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [result, setResult] = useState(null);
  const [downloadingReport, setDownloadingReport] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setResult(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selected = e.dataTransfer.files[0];
      setFile(selected);
      setResult(null);
    }
  };

  const startVerification = async () => {
    if (!file) {
      toast.error('Please upload a document file before proceeding.');
      return;
    }

    setIsVerifying(true);
    setProgressStep(1);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('candidate_name', candidateName || 'Direct Candidate');
    formData.append('document_title', file.name);

    try {
      const timer = setInterval(() => {
        setProgressStep((prev) => (prev < 4 ? prev + 1 : prev));
      }, 350);

      const res = await collegeService.verifyDirect(formData);
      clearInterval(timer);
      setProgressStep(5);
      setResult(res.data);

      const status = res.data?.final_status || res.data?.overall_status || res.data?.status;
      if (status === 'AUTHENTICATED') {
        toast.success('Document verified successfully: AUTHENTICATED');
      } else if (status === 'SUSPICIOUS') {
        toast.warning('Document verification completed: Document flagged as SUSPICIOUS');
      } else if (status === 'NOT_VERIFIED') {
        toast.info('Document verification completed: Document could not be verified (unknown or unrecognized document format)');
      } else {
        toast.info(`Document verification completed: ${status || 'COMPLETED'}`);
      }
    } catch (err) {
      toast.error(
        err.response?.data?.error ||
          err.message ||
          'Verification request failed. Please check network connection or server status.'
      );
    } finally {
      setIsVerifying(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!result?.report_id) {
      toast.error('Report certificate is not attached to this record.');
      return;
    }

    try {
      setDownloadingReport(true);
      const res = await reportService.downloadSingleReport(result.report_id);
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${result.report_id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Official PDF report downloaded!');
    } catch (err) {
      toast.error('Failed to download verification report.');
    } finally {
      setDownloadingReport(false);
    }
  };

  const resetVerification = () => {
    setFile(null);
    setResult(null);
    setCandidateName('');
    setProgressStep(0);
  };

  const progressLabels = [
    'Initializing verification...',
    'Step 1 of 4: Uploading Document...',
    'Step 2 of 4: OCR & Multimodal Data Extraction...',
    'Step 3 of 4: Evaluating 12 Modular Verification Checks...',
    'Step 4 of 4: Generating Security Report & Audit Hashes...',
    'Verification pipeline completed!'
  ];

  return (
    <div className="max-w-4xl space-y-6">
      <PageHeader
        title="Verify Documents"
        subtitle="Institutional verification console with automatic document identification and 12 deterministic multi-signal verification checks."
      />

      {/* AUTOMATIC CLASSIFICATION BANNER */}
      {!result && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-blue-600 text-white shrink-0 shadow-xs">
            <Sparkles className="w-5 h-5" />
          </div>
          <div className="text-xs">
            <h4 className="font-bold text-blue-900">Institutional Multi-Signal Verification Engine</h4>
            <p className="text-blue-700 mt-0.5">
              Upload candidate documents directly without manual category selection. The system automatically detects the document profile, validates numerical and field consistency, audits cryptographic integrity, and verifies against institutional records.
            </p>
          </div>
        </div>
      )}

      {/* DIRECT UPLOAD CONSOLE */}
      {!result && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
          {/* Candidate Name Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Candidate / Student Name (Optional for Walk-in Verification)
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <User className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={candidateName}
                onChange={(e) => setCandidateName(e.target.value)}
                placeholder="e.g., Rahul Sharma (or leave blank for auto-OCR extraction)"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50/50 border border-slate-300 rounded-xl text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600/20 focus:border-blue-600 transition-colors shadow-xs"
              />
            </div>
          </div>

          {/* Drag & Drop Area */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-8 sm:p-10 text-center cursor-pointer transition-all ${
              dragOver
                ? 'border-blue-500 bg-blue-50/50'
                : file
                ? 'border-emerald-300 bg-emerald-50/30'
                : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,.png,.jpg,.jpeg,.webp"
              className="hidden"
            />

            {file ? (
              <div className="space-y-2">
                <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto shadow-xs">
                  <FileText className="w-7 h-7" />
                </div>
                <h4 className="text-base font-bold text-slate-900">{file.name}</h4>
                <p className="text-xs text-slate-500">
                  {(file.size / 1024).toFixed(1)} KB • Click to change document
                </p>
                <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-100/80 text-emerald-800 rounded-full text-xs font-semibold mt-2">
                  <Sparkles className="w-3.5 h-3.5" />
                  Ready for Automatic Document Verification
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="w-14 h-14 rounded-2xl bg-slate-100 text-slate-600 flex items-center justify-center mx-auto">
                  <UploadCloud className="w-7 h-7" />
                </div>
                <div>
                  <h4 className="text-base font-bold text-slate-900">Drag and Drop Document Here</h4>
                  <p className="text-xs text-slate-500 mt-1">or click anywhere to browse from your device</p>
                </div>
                <p className="text-[11px] text-slate-400">Supported Formats: PDF, JPG, JPEG, PNG, WEBP (Max 10 MB)</p>
              </div>
            )}
          </div>

          {/* 4-Step Verification Progress Indicator */}
          {isVerifying && (
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-800 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                  {progressLabels[progressStep] || progressLabels[1]}
                </span>
                <span className="text-slate-500 font-mono text-[11px]">12 Verification Checks</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(progressStep * 25, 95)}%` }}
                />
              </div>
            </div>
          )}

          {/* Action Button */}
          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={startVerification}
              disabled={!file || isVerifying}
              className="inline-flex items-center gap-2 px-7 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:bg-slate-300 disabled:cursor-not-allowed"
            >
              {isVerifying ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Verifying Candidate Document...</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  <span>Verify Document</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* STANDARDIZED VERIFICATION RESULTS UI */}
      {result && (
        <VerificationResult
          result={result}
          reportId={result.report_id}
          documentTitle={file?.name}
          onDownloadReport={handleDownloadReport}
          onReset={resetVerification}
        />
      )}
    </div>
  );
};

export default CollegeVerification;
