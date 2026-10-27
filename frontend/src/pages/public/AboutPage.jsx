import React from 'react';
import { ShieldCheck, Award, Lock, FileText, CheckCircle2 } from 'lucide-react';
import PageHeader from '../../components/common/PageHeader';

export const AboutPage = () => {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      
      <PageHeader
        title="About Authentication Validator"
        subtitle="Comprehensive Document Verification & Integrity Architecture"
        badge="Enterprise Standard"
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
          <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-3">
            <Award className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 mb-1">Academic Integrity</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Eliminating academic credential forgery and unauthorized certificate alterations with automated multi-layer verification.
          </p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
          <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center mb-3">
            <Lock className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 mb-1">Dual Verification Paradigm</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            Independent student self-verification alongside direct institutional document authenticity validation.
          </p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs">
          <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center mb-3">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-slate-900 mb-1">Cryptographic Anchoring</h3>
          <p className="text-xs text-slate-600 leading-relaxed">
            SHA-256 document hashing and blockchain integrity auditing to guarantee non-repudiation.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-xs space-y-6">
        <h2 className="text-lg font-bold text-slate-900">Platform Objectives & Core Principles</h2>
        
        <div className="space-y-4 text-xs sm:text-sm text-slate-700 leading-relaxed">
          <p>
            The <strong>Authentication Validator</strong> is a verification platform developed to combat credential fraud during university admissions, employment screening, and official document validation.
          </p>
          <p>
            Rather than relying solely on manual visual inspection or centralized databases that may be unavailable or fragmented, our modular system evaluates multiple dimensions of authenticity simultaneously:
          </p>

          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs">
            <li className="flex items-start gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span><strong>OCR Analysis:</strong> Extracts text content and cross-references registration numbers, dates, and subject marks.</span>
            </li>
            <li className="flex items-start gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span><strong>Error Level Analysis (ELA):</strong> Identifies compression discrepancies in altered image blocks.</span>
            </li>
            <li className="flex items-start gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span><strong>QR Code Decoding:</strong> Matches encoded digital signatures with visual document text.</span>
            </li>
            <li className="flex items-start gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span><strong>Metadata Integrity:</strong> Flags modifications created using photo manipulation software.</span>
            </li>
          </ul>
        </div>
      </div>

    </div>
  );
};

export default AboutPage;
