import React from 'react';
import { UploadCloud, Cpu, CheckCircle, FileDown, ArrowRight, ShieldCheck, Building2, UserCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import PageHeader from '../../components/common/PageHeader';

export const HowItWorksPage = () => {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-12">
      
      <PageHeader
        title="How It Works"
        subtitle="Step-by-step walkthrough of the verification workflow for Students and Academic Institutions"
      />

      {/* Steps Visual */}
      <div className="space-y-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-xs flex flex-col md:flex-row gap-6 items-start">
          <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center font-bold text-lg shrink-0">
            01
          </div>
          <div className="flex-1 space-y-2">
            <h3 className="text-base font-bold text-slate-900">Document Upload & Hashing</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              The user (student or college admin) uploads a digital copy (PDF, JPG, PNG) of the academic document. The system immediately computes an unalterable SHA-256 cryptographic hash to ensure the original file cannot be tampered with during transit.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-xs flex flex-col md:flex-row gap-6 items-start">
          <div className="w-12 h-12 rounded-xl bg-amber-50 border border-amber-200 text-amber-600 flex items-center justify-center font-bold text-lg shrink-0">
            02
          </div>
          <div className="flex-1 space-y-2">
            <h3 className="text-base font-bold text-slate-900">Multi-Layer Verification Engine Execution</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              The file is routed through modular verification routines in parallel: OCR extracts critical fields, QR decoders parse secure barcodes, ELA algorithms inspect pixel compression variances for forgery, and metadata analyzers check creation headers.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-xs flex flex-col md:flex-row gap-6 items-start">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-600 flex items-center justify-center font-bold text-lg shrink-0">
            03
          </div>
          <div className="flex-1 space-y-2">
            <h3 className="text-base font-bold text-slate-900">Confidence Scoring & Verdict Determination</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              Each layer outputs an isolated status (Passed, Failed, or Not Applicable). If all critical checks succeed, the document is awarded an official <strong>Authenticated</strong> verdict. Any detected tampering flags the document as <strong>Suspicious</strong> or <strong>Not Authenticated</strong>.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 sm:p-8 shadow-xs flex flex-col md:flex-row gap-6 items-start">
          <div className="w-12 h-12 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-600 flex items-center justify-center font-bold text-lg shrink-0">
            04
          </div>
          <div className="flex-1 space-y-2">
            <h3 className="text-base font-bold text-slate-900">Report Generation & Blockchain Record</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              An official Certificate of Authenticity PDF report is generated featuring the verification seal, verification ID, timestamp, and document hash. The record is permanently recorded to verification history.
            </p>
          </div>
        </div>
      </div>

      {/* CTA Box */}
      <div className="bg-slate-900 text-white rounded-xl p-8 text-center space-y-4">
        <h3 className="text-lg font-bold">Ready to test the pipeline?</h3>
        <p className="text-xs text-slate-300 max-w-md mx-auto">
          Sign in to your account and upload a document to run instant authenticity verification.
        </p>
        <div className="flex justify-center gap-3 pt-2">
          <Link
            to="/student/login"
            className="px-4 py-2 rounded-lg bg-blue-600 text-white text-xs font-semibold hover:bg-blue-500 transition-colors"
          >
            Student Portal
          </Link>
          <Link
            to="/college/login"
            className="px-4 py-2 rounded-lg bg-slate-800 text-slate-200 border border-slate-700 text-xs font-semibold hover:bg-slate-700 transition-colors"
          >
            College Portal
          </Link>
        </div>
      </div>

    </div>
  );
};

export default HowItWorksPage;
