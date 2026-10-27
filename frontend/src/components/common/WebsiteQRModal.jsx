import React from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { QrCode, Download, Share2, Globe, ShieldCheck } from 'lucide-react';
import Modal from './Modal';

export const WebsiteQRModal = ({ isOpen, onClose }) => {
  const websiteUrl = window.location.origin;

  const handleDownload = () => {
    const svg = document.getElementById("website-qr-code");
    if (!svg) return;
    const svgData = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const img = new Image();
    img.onload = () => {
      canvas.width = img.width + 40;
      canvas.height = img.height + 40;
      if (ctx) {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 20, 20);
      }
      const pngFile = canvas.toDataURL("image/png");
      const downloadLink = document.createElement("a");
      downloadLink.download = "Authentication_Validator_Official_QR.png";
      downloadLink.href = pngFile;
      downloadLink.click();
    };
    img.src = "data:image/svg+xml;base64," + btoa(svgData);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Official Portal QR Code" maxWidth="max-w-md">
      <div className="flex flex-col items-center text-center">
        <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
          <Globe className="w-6 h-6" />
        </div>
        
        <h4 className="text-base font-bold text-slate-900">Scan to Access Portal</h4>
        <p className="text-xs text-slate-500 mt-1 max-w-xs">
          Scan this QR code with any mobile device to open the Authentication Validator platform.
        </p>

        <div className="my-6 p-4 bg-white rounded-2xl border-2 border-slate-200 shadow-sm">
          <QRCodeSVG
            id="website-qr-code"
            value={websiteUrl}
            size={200}
            level="H"
            includeMargin={true}
          />
        </div>

        <div className="flex items-center gap-1.5 px-3 py-1 bg-slate-100 rounded-full text-xs font-mono text-slate-600 mb-6 max-w-full truncate">
          <ShieldCheck className="w-3.5 h-3.5 text-blue-600 shrink-0" />
          <span className="truncate">{websiteUrl}</span>
        </div>

        <div className="flex items-center gap-3 w-full">
          <button
            onClick={handleDownload}
            className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors shadow-sm text-sm"
          >
            <Download className="w-4 h-4" />
            Download QR
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-xl transition-colors text-sm"
          >
            Close
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default WebsiteQRModal;
