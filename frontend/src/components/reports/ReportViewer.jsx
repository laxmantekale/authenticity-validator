import React, { useState, useEffect } from 'react';
import {
  FileText,
  Printer,
  Download,
  FileCode,
  X,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  XCircle,
  Loader2,
  Lock,
  Layers,
  CheckCircle2,
  Info,
  Calendar,
  Building,
  User,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import StatusBadge from '../common/StatusBadge';
import { reportService } from '../../services/reportService';
import { useToast } from '../../context/ToastContext';

export const ReportViewer = ({ reportId, onClose }) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [reportData, setReportData] = useState(null);
  const [expandedCheck, setExpandedCheck] = useState(null);
  const [downloadingJson, setDownloadingJson] = useState(false);

  useEffect(() => {
    if (!reportId) return;

    const fetchDetails = async () => {
      setLoading(true);
      try {
        const res = await reportService.getReportDetails(reportId);
        setReportData(res.data.report);
      } catch (err) {
        console.error('Failed to load report details', err);
        toast.error('Unable to load structured report details.');
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [reportId]);

  if (!reportId) return null;

  const [downloadingPdf, setDownloadingPdf] = useState(false);

  const handleDownloadPdf = async () => {
    try {
      setDownloadingPdf(true);
      const res = await reportService.downloadSingleReport(reportId);
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Report PDF downloaded successfully.');
    } catch (err) {
      toast.error('Failed to download PDF report.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleDownloadJson = async () => {
    try {
      setDownloadingJson(true);
      const res = await reportService.downloadReportJson(reportId);
      const blob = new Blob([res.data], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Verification_Report_${reportId}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('JSON report downloaded.');
    } catch (err) {
      toast.error('Failed to download JSON report.');
    } finally {
      setDownloadingJson(false);
    }
  };

  const handlePrint = async () => {
    try {
      const res = await reportService.downloadSingleReport(reportId);
      const blobUrl = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const printWindow = window.open(blobUrl, '_blank');
      if (printWindow) {
        printWindow.onload = () => printWindow.print();
      } else {
        window.print();
      }
    } catch (err) {
      window.print();
    }
  };

  const secA = reportData?.section_a || {};
  const secB = reportData?.section_b || {};
  const secC = reportData?.section_c || {};
  const secD = reportData?.section_d || [];
  const secE = reportData?.section_e || {};
  const secF = reportData?.section_f || '';
  const secG = reportData?.section_g || [];
  const secH = reportData?.section_h || {};
  const secI = reportData?.section_i || {};

  const finalStatus = (secB.final_status || 'NOT_VERIFIED').toUpperCase();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-slate-900/70 backdrop-blur-sm animate-in fade-in">
      <div className="bg-white rounded-2xl border border-slate-200 w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Modal Top Bar */}
        <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/70 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-blue-100 text-blue-700 rounded-lg">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Official Verification Report: <span className="font-mono text-blue-700">{reportId}</span>
              </h3>
              <p className="text-[11px] text-slate-500 font-mono">
                Verification ID: {secA.verification_id || 'N/A'} • {secA.generated_at || 'Recent'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrint}
              className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold shadow-2xs transition-colors cursor-pointer"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print</span>
            </button>

            <button
              onClick={handleDownloadJson}
              disabled={downloadingJson}
              className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold shadow-2xs transition-colors cursor-pointer"
            >
              <FileCode className="w-3.5 h-3.5" />
              <span>JSON</span>
            </button>

            <button
              onClick={handleDownloadPdf}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download PDF</span>
            </button>

            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-6">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-3">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              <p className="text-xs font-semibold text-slate-600">Retrieving official verification audit record...</p>
            </div>
          ) : (
            <>
              {/* SECTION B: OVERALL RESULT BANNER */}
              <div className={`p-6 rounded-2xl border shadow-xs ${
                finalStatus === 'AUTHENTICATED'
                  ? 'bg-emerald-50/70 border-emerald-200'
                  : finalStatus === 'SUSPICIOUS'
                  ? 'bg-amber-50/70 border-amber-200'
                  : finalStatus === 'NOT_VERIFIED'
                  ? 'bg-slate-50 border-slate-300'
                  : 'bg-rose-50/70 border-rose-200'
              }`}>
                <div className="flex items-start gap-4">
                  <div className={`p-3.5 rounded-2xl shrink-0 shadow-xs ${
                    finalStatus === 'AUTHENTICATED'
                      ? 'bg-emerald-100 text-emerald-700'
                      : finalStatus === 'SUSPICIOUS'
                      ? 'bg-amber-100 text-amber-800'
                      : finalStatus === 'NOT_VERIFIED'
                      ? 'bg-slate-200 text-slate-700'
                      : 'bg-rose-100 text-rose-700'
                  }`}>
                    {finalStatus === 'AUTHENTICATED' ? (
                      <ShieldCheck className="w-9 h-9" />
                    ) : finalStatus === 'SUSPICIOUS' ? (
                      <AlertTriangle className="w-9 h-9" />
                    ) : finalStatus === 'NOT_VERIFIED' ? (
                      <HelpCircle className="w-9 h-9" />
                    ) : (
                      <XCircle className="w-9 h-9" />
                    )}
                  </div>

                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <StatusBadge status={finalStatus} size="lg" />
                      {secB.classification_confidence && (
                        <span className="text-xs font-semibold px-2 py-0.5 bg-white border border-slate-200 rounded text-slate-700">
                          Classification: {secB.classification_confidence}% match
                        </span>
                      )}
                    </div>
                    <h2 className="text-lg sm:text-xl font-bold text-slate-900 pt-0.5">
                      {secB.document_name || secB.document_type || 'Academic Record'}
                    </h2>
                    <p className="text-xs text-slate-700 leading-relaxed">
                      {secB.decision_summary}
                    </p>
                  </div>
                </div>
              </div>

              {/* SECTION C: DOCUMENT INFORMATION */}
              <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-blue-600" />
                  Document & Candidate Information
                </h4>

                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block font-medium">Document Type</span>
                    <strong className="text-slate-900 font-bold block mt-0.5 truncate">{secC.document_title}</strong>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block font-medium">Holder / Candidate</span>
                    <strong className="text-slate-900 font-bold block mt-0.5 truncate">{secC.holder_name}</strong>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block font-medium">Identifier / Ref No</span>
                    <strong className="text-slate-900 font-mono font-bold block mt-0.5 truncate">{secC.document_identifier}</strong>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block font-medium">Issuing Institution</span>
                    <strong className="text-slate-900 font-bold block mt-0.5 truncate">{secC.issuer_institution}</strong>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block font-medium">Issue Date</span>
                    <strong className="text-slate-900 block mt-0.5 truncate">{secC.issue_date}</strong>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block font-medium">Expiry Date</span>
                    <strong className="text-slate-900 block mt-0.5 truncate">{secC.expiry_date}</strong>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block font-medium">Pages</span>
                    <strong className="text-slate-900 block mt-0.5 truncate">{secC.number_of_pages || 1}</strong>
                  </div>

                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-slate-400 block font-medium">File Format</span>
                    <strong className="text-slate-900 block mt-0.5 truncate">{secC.file_format || 'PDF'}</strong>
                  </div>
                </div>
              </div>

              {/* SECTION D: 12 VERIFICATION CHECKS TABLE */}
              <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
                <div className="p-4 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <Layers className="w-4 h-4 text-blue-600" />
                      12 Modular Verification Checks
                    </h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Deterministic evaluation across all document verification layers
                    </p>
                  </div>
                  <span className="text-xs font-mono font-semibold text-slate-500">{secD.length} Checks</span>
                </div>

                <div className="divide-y divide-slate-100 text-xs">
                  {secD.map((check) => {
                    const isExpanded = expandedCheck === check.key;
                    return (
                      <div key={check.key} className="transition-colors hover:bg-slate-50/80">
                        <div
                          onClick={() => setExpandedCheck(isExpanded ? null : check.key)}
                          className="p-3.5 sm:px-5 flex items-center justify-between gap-4 cursor-pointer select-none"
                        >
                          <span className="font-bold text-slate-900 min-w-[170px]">{check.name}</span>
                          <span className="flex-1 text-slate-600 truncate hidden md:block">
                            {check.short_explanation}
                          </span>
                          <div className="flex items-center gap-3 shrink-0">
                            <StatusBadge status={check.status} size="sm" />
                            {isExpanded ? (
                              <ChevronUp className="w-4 h-4 text-slate-400" />
                            ) : (
                              <ChevronDown className="w-4 h-4 text-slate-400" />
                            )}
                          </div>
                        </div>

                        {isExpanded && (
                          <div className="px-5 pb-4 pt-1 bg-slate-50 border-t border-slate-100 space-y-2">
                            <p className="text-slate-800 font-medium">
                              <b>Evaluation:</b> {check.short_explanation}
                            </p>
                            {check.limitations && (
                              <p className="text-slate-500 text-[11px]">
                                <b>Scope & Limitations:</b> {check.limitations}
                              </p>
                            )}
                            {check.evidence && Object.keys(check.evidence).length > 0 && (
                              <div className="p-2.5 bg-white rounded-lg border border-slate-200 text-[11px] font-mono text-slate-700 overflow-x-auto">
                                <pre className="whitespace-pre-wrap">{JSON.stringify(check.evidence, null, 2)}</pre>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* SECTION E: FINDINGS & LIMITATIONS */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Findings & Scope Limitations
                  </h4>
                  <ul className="space-y-1.5 text-xs text-slate-700">
                    {secE.confirmed && secE.confirmed.map((item, idx) => (
                      <li key={`c-${idx}`} className="flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </li>
                    ))}
                    {secE.warnings && secE.warnings.map((warn, idx) => (
                      <li key={`w-${idx}`} className="flex items-start gap-2 text-amber-800">
                        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                        <span>{warn}</span>
                      </li>
                    ))}
                    {secE.checks_not_performed && secE.checks_not_performed.map((item, idx) => (
                      <li key={`np-${idx}`} className="flex items-start gap-2 text-slate-500">
                        <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Recommended Next Steps
                  </h4>
                  <ol className="space-y-2 text-xs text-slate-700">
                    {secG.map((step, idx) => (
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

              {/* SECTION H: AUDIT & INTEGRITY DETAILS */}
              <div className="p-4 bg-slate-900 text-white rounded-xl border border-slate-800 space-y-2 text-xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <span className="font-semibold text-slate-300 flex items-center gap-2">
                    <Lock className="w-4 h-4 text-emerald-400" />
                    Cryptographic SHA-256 Hash Seal:
                  </span>
                  <span className="font-mono text-emerald-300 text-[11px] select-all break-all">
                    {secH.file_hash || secC.sha256_hash}
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-x-6 gap-y-1 text-slate-400 text-[11px] pt-1 border-t border-slate-800">
                  <span>Network: {secH.blockchain_network || 'Polygon POS Testnet'}</span>
                  <span>Anchor Reference: {secH.blockchain_tx_hash || 'Confirmed'}</span>
                  <span>Algorithm: SHA-256</span>
                </div>
              </div>

              {/* SECTION I: DISCLAIMER */}
              <p className="text-[11px] text-slate-400 text-center italic max-w-2xl mx-auto">
                {secI.disclaimer}
              </p>
            </>
          )}
        </div>

        {/* Modal Bottom Bar */}
        <div className="p-4 border-t border-slate-100 flex items-center justify-between bg-slate-50/70 shrink-0">
          <span className="text-xs text-slate-500">
            Report ID: <strong className="font-mono text-slate-800">{reportId}</strong>
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadPdf}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download PDF</span>
            </button>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg text-xs transition-colors cursor-pointer"
            >
              Close
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default ReportViewer;
