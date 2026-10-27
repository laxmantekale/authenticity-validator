import React, { useEffect, useRef, useState } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { QrCode, AlertCircle, Camera } from 'lucide-react';

export const QRScanner = ({ onScanSuccess, onScanError }) => {
  const [scanResult, setScanResult] = useState('');
  const [error, setError] = useState('');
  const scannerRef = useRef(null);

  useEffect(() => {
    const scanner = new Html5QrcodeScanner(
      "qr-reader-container",
      {
        fps: 10,
        qrbox: { width: 250, height: 250 },
        rememberLastUsedCamera: true
      },
      false
    );

    scanner.render(
      (decodedText) => {
        setScanResult(decodedText);
        if (onScanSuccess) {
          onScanSuccess(decodedText);
        }
      },
      (errorMessage) => {
        if (onScanError) {
          onScanError(errorMessage);
        }
      }
    );

    return () => {
      try {
        scanner.clear();
      } catch (e) {}
    };
  }, [onScanSuccess, onScanError]);

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
      <div className="flex items-center gap-2">
        <Camera className="w-5 h-5 text-emerald-600" />
        <h3 className="text-sm font-bold text-slate-900">Scan College Connection QR Code</h3>
      </div>

      <div id="qr-reader-container" className="w-full rounded-xl overflow-hidden border border-slate-200" />

      {scanResult && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 font-mono break-all">
          <b>Decoded:</b> {scanResult}
        </div>
      )}
    </div>
  );
};

export default QRScanner;
