import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  FileText,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  FileSearch,
  QrCode,
  Feather,
  Stamp,
  FileCode,
  Download,
  Loader2,
  RefreshCw,
  ArrowRight,
  Cpu,
  Layers,
  Sparkles,
  Database,
  Link as LinkIcon,
  Barcode,
  Lock,
  Search,
  Check,
  Building2,
  Calendar
} from 'lucide-react';
import { verificationService } from '../../services/verificationService';
import { reportService } from '../../services/reportService';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import SectionCard from '../../components/common/SectionCard';
import StatusBadge from '../../components/common/StatusBadge';
import VerificationResult from '../../components/verification/VerificationResult';

export const VerifyDocument = () => {
  const { toast } = useToast();
  const fileInputRef = useRef(null);

  const [file, setFile] = useState(null);
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
    formData.append('document_title', file.name);

    try {
      // Step interval animation for clean feedback
      const timer = setInterval(() => {
        setProgressStep((prev) => (prev < 4 ? prev + 1 : prev));
      }, 350);

      const res = await verificationService.verifyStudentDirect(formData);
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
      toast.error(err.response?.data?.error || err.message || 'Verification request failed. Please check network connection or server status.');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!result?.report_id) {
      toast.error('Report not found for this verification.');
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
    setProgressStep(0);
  };

  return (
    <div className="max-w-4xl space-y-6">
      
      <PageHeader
        title="Verify Document"
        subtitle="Upload your document. The verification pipeline automatically identifies the document category and validates authenticity across 8 deterministic multi-signal verification checks."
      />

      {/* AUTOMATIC DOCUMENT IDENTIFICATION BANNER */}
      {!result && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 rounded-xl p-4 flex items-center gap-3">
          <div className="p-2.5 rounded-lg bg-blue-600 text-white shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
          <div className="text-xs">
            <h4 className="font-bold text-blue-900">Automatic Document Identification & Multi-Signal Engine</h4>
            <p className="text-blue-700 mt-0.5">
              No manual category selection required. Upload your document file and our verification engine will automatically identify the document format, verify field consistency, check QR/barcodes, inspect cryptographic integrity, and evaluate official registry alignment.
            </p>
          </div>
        </div>
      )}

      {/* UPLOAD & VERIFY CONSOLE */}
      {!result && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-6">
          
          {/* Drag & Drop Area */}
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
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
                <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB • Click to change file</p>
                <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-100/80 text-emerald-800 rounded-full text-xs font-semibold mt-2">
                  <Sparkles className="w-3.5 h-3.5" />
                  Ready for Automatic Document Identification
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

          {/* Verification Progress Indicator */}
          {isVerifying && (
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-800 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                  {progressStep === 1
                    ? 'Step 1 of 4: Uploading Document...'
                    : progressStep === 2
                    ? 'Step 2 of 4: OCR & Multimodal Extraction...'
                    : progressStep === 3
                    ? 'Step 3 of 4: Evaluating 12 Verification Checks...'
                    : progressStep >= 4
                    ? 'Step 4 of 4: Generating Security Report...'
                    : 'Running Verification Pipeline...'}
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
                  <span>Verifying Document...</span>
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

      {/* VERIFICATION RESULTS UI */}
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

export default VerifyDocument;
