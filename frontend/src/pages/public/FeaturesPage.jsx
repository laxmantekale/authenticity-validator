import React from 'react';
import {
  FileSearch,
  QrCode,
  ShieldAlert,
  Feather,
  Stamp,
  FileCode,
  Database,
  Link2,
  CheckCircle2
} from 'lucide-react';
import PageHeader from '../../components/common/PageHeader';

export const FeaturesPage = () => {
  const modules = [
    {
      title: 'Tesseract OCR Text Extraction',
      desc: 'Accurately parses document text headers, student names, registration numbers, GPA scores, and issuance dates.',
      icon: FileSearch,
      tag: 'Text Layer'
    },
    {
      title: 'QR Code Signature Matching',
      desc: 'Decodes embedded QR barcodes, verifies public keys, and cross-references payload against visual text fields.',
      icon: QrCode,
      tag: 'Cryptographic Layer'
    },
    {
      title: 'Tampering & Metadata Detection',
      desc: 'Detects digital alterations, software manipulations, cloned elements, and compression disparities.',
      icon: ShieldAlert,
      tag: 'Integrity Layer'
    },
    {
      title: 'Signature Contour Verification',
      desc: 'Detects authorized signature boundaries, evaluates stroke density, and flags pasted signatures.',
      icon: Feather,
      tag: 'Biometric Layer'
    },
    {
      title: 'Institutional Stamp & Seal Validation',
      desc: 'Identifies circular and rectangular institutional seals and validates color profile consistency.',
      icon: Stamp,
      tag: 'Seal Layer'
    },
    {
      title: 'PDF & EXIF Metadata Analysis',
      desc: 'Scans file headers for editing software artifacts (Photoshop, Canva, GIMP) and altered creation timestamps.',
      icon: FileCode,
      tag: 'Metadata Layer'
    },
    {
      title: 'Institutional Database Cross-Reference',
      desc: 'When connected to an authorized college, cross-verifies student enrollment and marksheet serial numbers.',
      icon: Database,
      tag: 'Database Layer'
    },
    {
      title: 'Blockchain Verification Ledger',
      desc: 'Anchors verified document hashes onto decentralized network to provide public verification proof.',
      icon: Link2,
      tag: 'Trust Layer'
    }
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      <PageHeader
        title="Verification Features & Technologies"
        subtitle="Comprehensive breakdown of our intelligent academic document authenticity validation pipeline"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {modules.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div key={idx} className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs flex gap-4 items-start">
              <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-800 border border-slate-200 flex items-center justify-center shrink-0 mt-0.5">
                <Icon className="w-5 h-5" />
              </div>
              <div className="flex-1 space-y-1.5">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900">{m.title}</h3>
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                    {m.tag}
                  </span>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">{m.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default FeaturesPage;
