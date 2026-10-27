import React from 'react';
import { Download, Building2, Printer, ShieldCheck } from 'lucide-react';
import QRGenerator from './QRGenerator';

export const CollegeQRCard = ({ college, qrData }) => {
  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6 text-center max-w-md mx-auto">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold border border-emerald-200">
        <ShieldCheck className="w-3.5 h-3.5" />
        Official Institutional QR Token
      </div>

      <div>
        <h2 className="text-lg font-bold text-slate-900">{college?.college_name || 'Academic Institution'}</h2>
        <p className="text-xs text-slate-500 font-mono mt-0.5">ID: {college?.college_id || 'COL101'}</p>
      </div>

      <div className="flex justify-center py-2">
        <QRGenerator value={qrData?.connect_url || 'https://authenticity-validator.edu.in'} size={220} />
      </div>

      <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-600 font-mono break-all text-left">
        <p className="text-[10px] text-slate-400 uppercase font-bold mb-1">Secure Connect Link</p>
        <p>{qrData?.connect_url || 'N/A'}</p>
      </div>

      <div className="flex items-center justify-center gap-3 pt-2">
        <button
          onClick={handlePrint}
          className="inline-flex items-center gap-1.5 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-xs font-semibold shadow-sm transition-colors"
        >
          <Printer className="w-4 h-4" />
          Print Signage
        </button>
      </div>
    </div>
  );
};

export default CollegeQRCard;
