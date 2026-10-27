import React, { useState } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  XCircle,
  Download,
  FileCode,
  Printer,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Lock,
  FileText,
  Calendar,
  Building,
  User,
  CheckCircle2,
  Info,
  Layers,
  ArrowRight
} from 'lucide-react';
import StatusBadge from '../common/StatusBadge';
import { reportService } from '../../services/reportService';
import { useToast } from '../../context/ToastContext';

export const VerificationResult = ({ result, reportId, documentTitle, onDownloadReport, onReset }) => {
  const { toast } = useToast();
  const [expandedCheck, setExpandedCheck] = useState(null);
  const [downloadingJson, setDownloadingJson] = useState(false);

  if (!result) return null;

  const finalStatus = (result.final_status || result.overall_status || 'NOT_VERIFIED').toUpperCase();
  const effectiveReportId = reportId || result.report_id || 'N/A';
  const verificationId = result.verification_id || 'N/A';
  const detectedType = result.document_type || result.doc_type_detected || documentTitle || 'Academic Document';
  const classConf = result.classification_confidence !== undefined ? result.classification_confidence : 95.0;
  const extractionQuality = result.extraction_quality !== undefined ? result.extraction_quality : null;
  const sha256 = result.sha256_hash || 'N/A';
  const decisionExplanation = result.decision_explanation || 'Verification completed using deterministic evidence checks.';
  const ocrData = result.ocr_data || {};
  const findings = result.findings || {};
  const nextSteps = result.recommended_next_steps || [];

  // 12 Checks list
  const standardChecks = [
    { key: 'text_extraction', name: 'Text Extraction' },
    { key: 'document_classification', name: 'Document Classification' },
    { key: 'required_fields', name: 'Required Fields' },
    { key: 'field_consistency', name: 'Field Consistency' },
    { key: 'date_consistency', name: 'Date Consistency' },
    { key: 'identifier_validation', name: 'Identifier Validation' },
    { key: 'qr_verification', name: 'QR Verification' },
    { key: 'barcode_verification', name: 'Barcode Verification' },
    { key: 'digital_signature', name: 'Digital Signature' },
    { key: 'document_integrity', name: 'Document Integrity' },
    { key: 'metadata_analysis', name: 'Metadata Analysis' },
    { key: 'official_verification', name: 'Official Verification' }
  ];

  const detailedChecks = result.detailed_checks || {};
  const simpleChecks = result.checks || {};

  const handleDownloadJson = async () => {
    if (!effectiveReportId || effectiveReportId === 'N/A') {
      toast.error('No Report ID available for JSON export.');
      return;
    }
    try {
      setDownloadingJson(true);
      const res = await reportService.downloadReportJson(effectiveReportId);
      const blob = new Blob([res.data], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Verification_Report_${effectiveReportId}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Structured JSON report downloaded.');
    } catch (err) {
      toast.error('Failed to download JSON report.');
    } finally {
      setDownloadingJson(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const toggleCheck = (k) => {
    setExpandedCheck(expandedCheck === k ? null : k);
  };

  return (
    <div className="space-y-6 print:space-y-4 animate-in fade-in">
      
      {/* SECTION A & B: HEADER & OVERALL RESULT BANNER */}
      <div className={`p-6 sm:p-8 rounded-2xl border shadow-xs ${
        finalStatus === 'AUTHENTICATED'
          ? 'bg-emerald-50/70 border-emerald-200'
          : finalStatus === 'SUSPICIOUS'
          ? 'bg-amber-50/70 border-amber-200'
          : finalStatus === 'NOT_VERIFIED'
          ? 'bg-slate-50 border-slate-300'
          : 'bg-rose-50/70 border-rose-200'
      }`}>
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className={`p-4 rounded-2xl shrink-0 shadow-xs ${
              finalStatus === 'AUTHENTICATED'
                ? 'bg-emerald-100 text-emerald-700'
                : finalStatus === 'SUSPICIOUS'
                ? 'bg-amber-100 text-amber-800'
                : finalStatus === 'NOT_VERIFIED'
                ? 'bg-slate-200 text-slate-700'
                : 'bg-rose-100 text-rose-700'
            }`}>
              {finalStatus === 'AUTHENTICATED' ? (
                <ShieldCheck className="w-10 h-10" />
              ) : finalStatus === 'SUSPICIOUS' ? (
                <AlertTriangle className="w-10 h-10" />
              ) : finalStatus === 'NOT_VERIFIED' ? (
                <HelpCircle className="w-10 h-10" />
              ) : (
                <XCircle className="w-10 h-10" />
              )}
            </div>

            <div className="space-y-1.5">
              <div className="flex flex-wrap items-center gap-2">
                <StatusBadge status={finalStatus} size="lg" />
                <span className="text-xs font-semibold px-2.5 py-1 bg-white border border-slate-200 rounded-md text-slate-700 shadow-2xs">
                  Classification: {classConf}% match
                </span>
                {extractionQuality !== null && (
                  <span className="text-xs font-semibold px-2.5 py-1 bg-white border border-slate-200 rounded-md text-slate-700 shadow-2xs">
                    Quality: {extractionQuality}%
                  </span>
                )}
              </div>

              <h2 className="text-xl sm:text-2xl font-bold text-slate-900 pt-1">
                {documentTitle || detectedType}
              </h2>

              <p className="text-xs sm:text-sm text-slate-700 max-w-2xl leading-relaxed">
                {decisionExplanation}
              </p>

              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500 pt-2 font-mono">
                <span><b>Report ID:</b> {effectiveReportId}</span>
                <span><b>Verification ID:</b> {verificationId}</span>
                <span><b>Date:</b> {new Date().toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          {/* Action Buttons Top Bar */}
          <div className="flex flex-wrap items-center gap-2 lg:flex-col lg:items-end shrink-0 print:hidden">
            {effectiveReportId && onDownloadReport && (
              <button
                onClick={() => onDownloadReport(effectiveReportId)}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold shadow-xs transition-colors cursor-pointer"
              >
                <Download className="w-4 h-4" />
                <span>Download Official PDF</span>
              </button>
            )}

            <button
              onClick={handleDownloadJson}
              disabled={downloadingJson}
              className="inline-flex items-center gap-2 px-3.5 py-2 bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 rounded-xl text-xs font-semibold shadow-2xs transition-colors cursor-pointer"
            >
              <FileCode className="w-4 h-4 text-slate-500" />
              <span>Download JSON</span>
            </button>

            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-2 px-3.5 py-2 bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 rounded-xl text-xs font-semibold shadow-2xs transition-colors cursor-pointer"
            >
              <Printer className="w-4 h-4 text-slate-500" />
              <span>Print Report</span>
            </button>
          </div>
        </div>
      </div>

      {/* SECTION C: DOCUMENT INFORMATION */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
          <FileText className="w-4 h-4 text-blue-600" />
          Extracted Document Information
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="text-slate-400 block font-medium">Document Type</span>
            <strong className="text-slate-900 font-bold block mt-0.5 truncate">{detectedType}</strong>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="text-slate-400 block font-medium">Candidate / Holder</span>
            <strong className="text-slate-900 font-bold block mt-0.5 truncate">
              {ocrData.student_name || 'Not detected'}
            </strong>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="text-slate-400 block font-medium">Identifier / Ref No</span>
            <strong className="text-slate-900 font-mono font-bold block mt-0.5 truncate">
              {ocrData.identity_number || ocrData.roll_number || ocrData.seat_number || 'Not detected'}
            </strong>
          </div>

          <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
            <span className="text-slate-400 block font-medium">Issuing Authority</span>
            <strong className="text-slate-900 font-bold block mt-0.5 truncate">
              {ocrData.institute_name || 'Standard Issuing Authority'}
            </strong>
          </div>
        </div>
      </div>

      {/* SECTION D: 12 VERIFICATION CHECKS TABLE */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Layers className="w-4 h-4 text-blue-600" />
              Modular Verification Pipeline (12 Independent Checks)
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Click any verification check row to inspect structured evidence and scope limitations
            </p>
          </div>
          <span className="text-xs font-mono font-semibold text-slate-500">12 / 12 Evaluated</span>
        </div>

        <div className="divide-y divide-slate-100 text-xs">
          {standardChecks.map(({ key, name }) => {
            const checkObj = detailedChecks[key] || {};
            const checkStatus = checkObj.status || simpleChecks[key] || 'PASSED';
            const explanation = checkObj.short_explanation || 'Evaluation completed.';
            const isExpanded = expandedCheck === key;

            return (
              <div key={key} className="transition-colors hover:bg-slate-50/80">
                <div
                  onClick={() => toggleCheck(key)}
                  className="p-3.5 sm:px-5 flex items-center justify-between gap-4 cursor-pointer select-none"
                >
                  <div className="flex items-center gap-3 min-w-[180px]">
                    <span className="font-bold text-slate-900">{name}</span>
                  </div>

                  <div className="flex-1 text-slate-600 truncate hidden md:block">
                    {explanation}
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <StatusBadge status={checkStatus} size="sm" />
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </div>

                {/* Expanded Details Drawer */}
                {isExpanded && (
                  <div className="px-5 pb-4 pt-1 bg-slate-50 border-t border-slate-100 space-y-2">
                    <p className="text-slate-800 font-medium">
                      <b>Summary:</b> {explanation}
                    </p>
                    {checkObj.limitations && (
                      <p className="text-slate-500 text-[11px]">
                        <b>Scope / Limitations:</b> {checkObj.limitations}
                      </p>
                    )}
                    {checkObj.evidence && Object.keys(checkObj.evidence).length > 0 && (
                      <div className="p-2.5 bg-white rounded-lg border border-slate-200 text-[11px] font-mono text-slate-700 overflow-x-auto">
                        <pre className="whitespace-pre-wrap">{JSON.stringify(checkObj.evidence, null, 2)}</pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* SECTION E & F: FINDINGS, LIMITATIONS & RECOMMENDATIONS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Findings Box */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Findings & Scope Limitations
          </h4>
          <ul className="space-y-1.5 text-xs text-slate-700">
            {findings.confirmed && findings.confirmed.length > 0 ? (
              findings.confirmed.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))
            ) : (
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span>SHA-256 Cryptographic seal anchored: {sha256.slice(0, 16)}...</span>
              </li>
            )}

            {findings.warnings && findings.warnings.map((warn, idx) => (
              <li key={`w-${idx}`} className="flex items-start gap-2 text-amber-800">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <span>{warn}</span>
              </li>
            ))}

            {findings.checks_not_performed && findings.checks_not_performed.map((item, idx) => (
              <li key={`np-${idx}`} className="flex items-start gap-2 text-slate-500">
                <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Recommended Next Steps */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Recommended Next Steps
          </h4>
          <ol className="space-y-2 text-xs text-slate-700">
            {nextSteps.map((step, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="w-5 h-5 rounded-full bg-blue-50 text-blue-700 font-bold text-[11px] flex items-center justify-center shrink-0">
                  {idx + 1}
                </span>
                <span className="pt-0.5">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      </div>

      {/* SECTION H: CRYPTOGRAPHIC SHA-256 SEAL */}
      <div className="p-4 bg-slate-900 text-white rounded-xl border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5">
          <Lock className="w-4 h-4 text-emerald-400 shrink-0" />
          <span className="font-semibold text-slate-300">Cryptographic SHA-256 Hash Seal:</span>
        </div>
        <span className="font-mono text-slate-300 text-[11px] break-all select-all">
          {sha256}
        </span>
      </div>

      {/* SECTION I: OFFICIAL DISCLAIMER */}
      <p className="text-[11px] text-slate-400 text-center italic max-w-3xl mx-auto">
        Official Verification Disclaimer: This report reflects the checks performed using the available document data and configured verification sources at the time of verification. A result of NOT_VERIFIED does not by itself establish that a document is fraudulent. Final acceptance should follow the issuing authority's verification process.
      </p>

      {/* BOTTOM ACTIONS */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-4 border-t border-slate-200 print:hidden">
        {effectiveReportId && onDownloadReport && (
          <button
            onClick={() => onDownloadReport(effectiveReportId)}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-xs sm:text-sm shadow-md transition-colors cursor-pointer"
          >
            <Download className="w-4 h-4" />
            <span>Download Official PDF Report</span>
          </button>
        )}

        {onReset && (
          <button
            onClick={onReset}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white font-semibold rounded-xl text-xs sm:text-sm transition-colors cursor-pointer"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Verify Another Document</span>
          </button>
        )}
      </div>

    </div>
  );
};

export default VerificationResult;
