import React, { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { QrCode, Download, Printer, Share2, RefreshCw, CheckCircle2, ShieldCheck, Copy, ExternalLink } from 'lucide-react';
import api from '../../services/api';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import SectionCard from '../../components/common/SectionCard';
import LoadingState from '../../components/common/LoadingState';
import ConfirmationModal from '../../components/common/ConfirmationModal';

export const CollegeQR = () => {
  const { toast } = useToast();
  const [qrData, setQrData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [showRegenerateModal, setShowRegenerateModal] = useState(false);
  const [copied, setCopied] = useState(false);

  const fetchQR = async () => {
    try {
      setLoading(true);
      const res = await api.get('/college/qr');
      setQrData(res.data);
    } catch (err) {
      console.error('Failed to load college QR', err);
      toast.error('Unable to fetch institutional QR configuration.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQR();
  }, []);

  const handleDownload = () => {
    const svg = document.getElementById("college-qr-code-svg");
    if (!svg) return;
    const svgData = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const img = new Image();
    img.onload = () => {
      canvas.width = img.width + 60;
      canvas.height = img.height + 60;
      if (ctx) {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 30, 30);
      }
      const pngFile = canvas.toDataURL("image/png");
      const downloadLink = document.createElement("a");
      downloadLink.download = `${qrData?.college_code || 'COLLEGE'}_Official_QR.png`;
      downloadLink.href = pngFile;
      downloadLink.click();
      toast.success('Official Institutional QR Code downloaded.');
    };
    img.src = "data:image/svg+xml;base64," + btoa(svgData);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleCopyLink = () => {
    if (qrData?.connect_url) {
      navigator.clipboard.writeText(qrData.connect_url);
      setCopied(true);
      toast.success('Admissions Connect link copied to clipboard!');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRegenerateConfirm = async () => {
    setRegenerating(true);
    try {
      await api.post('/college/qr/regenerate');
      await fetchQR();
      toast.success('New institutional QR security token generated.');
      setShowRegenerateModal(false);
    } catch (err) {
      console.error('Failed to regenerate QR', err);
      toast.error('Failed to regenerate QR token.');
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return <LoadingState message="Generating institutional QR security pass..." />;
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <PageHeader
        title="Official Institution QR & Portal Link"
        subtitle="Display or distribute this QR code on admission notices, campus posters, and official websites for student linking"
        actions={
          <button
            onClick={() => setShowRegenerateModal(true)}
            disabled={regenerating}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-700 hover:text-slate-900 bg-white border border-slate-200 rounded-lg shadow-xs disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${regenerating ? 'animate-spin' : ''}`} />
            <span>Regenerate Token</span>
          </button>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* QR Code Presentation Box */}
        <div className="md:col-span-2 bg-white rounded-xl border border-slate-200 p-8 shadow-xs text-center space-y-6">
          <div>
            <span className="text-[11px] font-bold font-mono px-3 py-1 bg-blue-50 text-blue-700 rounded-full border border-blue-200">
              {qrData?.college_code}
            </span>
            <h2 className="text-xl font-bold text-slate-900 mt-2">{qrData?.college_name}</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Accredited Institution Verification & Admissions Portal
            </p>
          </div>

          {/* QR Container */}
          <div className="inline-block p-6 bg-white rounded-2xl border-2 border-slate-200 shadow-sm">
            {qrData?.connect_url && (
              <QRCodeSVG
                id="college-qr-code-svg"
                value={qrData.connect_url}
                size={220}
                level="H"
                includeMargin={true}
              />
            )}
          </div>

          {/* Token display */}
          <div className="max-w-md mx-auto p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs font-mono text-slate-600 space-y-1 text-left">
            <p className="truncate"><b>Security Token:</b> {qrData?.qr_token}</p>
            <p className="truncate text-[11px] text-slate-400"><b>Portal URL:</b> {qrData?.connect_url}</p>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap items-center justify-center gap-3 pt-4 border-t border-slate-100">
            <button
              onClick={handleDownload}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg text-xs sm:text-sm transition-colors shadow-xs"
            >
              <Download className="w-4 h-4" />
              <span>Download High-Res PNG</span>
            </button>

            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold rounded-lg text-xs sm:text-sm transition-colors"
            >
              <Printer className="w-4 h-4" />
              <span>Print Poster</span>
            </button>

            <button
              onClick={handleCopyLink}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 font-semibold rounded-lg text-xs sm:text-sm transition-colors"
            >
              {copied ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? 'Link Copied!' : 'Copy Direct Link'}</span>
            </button>
          </div>
        </div>

        {/* Sidebar Info / Security Guidance */}
        <div className="space-y-4">
          <SectionCard title="How QR Linking Works">
            <div className="space-y-3 text-xs text-slate-600">
              <div className="flex items-start gap-2.5">
                <span className="w-5 h-5 rounded-full bg-blue-50 text-blue-700 font-bold flex items-center justify-center shrink-0 text-[11px]">1</span>
                <p>Candidate scans your QR using mobile camera or visits the admissions URL.</p>
              </div>
              <div className="flex items-start gap-2.5">
                <span className="w-5 h-5 rounded-full bg-blue-50 text-blue-700 font-bold flex items-center justify-center shrink-0 text-[11px]">2</span>
                <p>System displays institutional profile and prompts student login / registration.</p>
              </div>
              <div className="flex items-start gap-2.5">
                <span className="w-5 h-5 rounded-full bg-blue-50 text-blue-700 font-bold flex items-center justify-center shrink-0 text-[11px]">3</span>
                <p>Student confirms link request. The request appears under <b>Student Requests</b> for verification.</p>
              </div>
            </div>
          </SectionCard>

          <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-200 text-xs text-emerald-900 space-y-2">
            <div className="flex items-center gap-1.5 font-bold text-emerald-800">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Zero Automatic Enrollment</span>
            </div>
            <p className="leading-relaxed text-[11px]">
              Scanning the QR only establishes a pending application. Candidate marksheets are only linked once approved by institutional authorities.
            </p>
          </div>
        </div>
      </div>

      <ConfirmationModal
        isOpen={showRegenerateModal}
        onClose={() => setShowRegenerateModal(false)}
        onConfirm={handleRegenerateConfirm}
        title="Regenerate Institutional QR Token"
        message="Are you sure you want to regenerate this QR code? Any previously printed posters will be permanently invalidated and will redirect students to a renewed link."
        confirmText="Regenerate Security Token"
        confirmVariant="danger"
        loading={regenerating}
      />
    </div>
  );
};

export default CollegeQR;
