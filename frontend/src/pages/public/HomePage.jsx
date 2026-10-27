import React from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  FileSearch,
  QrCode,
  Sparkles,
  Lock,
  Building2,
  ArrowRight,
  CheckCircle2,
  UserCheck,
  UploadCloud,
  Cpu,
  FileCheck2,
  FileDown
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const HomePage = () => {
  const { user, isStudent, isCollege } = useAuth();

  const features = [
    {
      title: 'Evidence-Based Document Verification',
      desc: 'Deterministic multi-signal document structure validation and authenticity verification.',
      icon: ShieldCheck,
      color: 'blue'
    },
    {
      title: 'QR Verification',
      desc: 'High-density encrypted QR code decoding matched directly against embedded credentials.',
      icon: QrCode,
      color: 'emerald'
    },
    {
      title: 'OCR Verification',
      desc: 'High-precision optical character recognition extracting names, serials, and academic scores.',
      icon: FileSearch,
      color: 'amber'
    },
    {
      title: 'Forgery Detection',
      desc: 'Error Level Analysis (ELA) and neural image tampering detection identifying modified regions.',
      icon: ShieldCheck,
      color: 'rose'
    },
    {
      title: 'Secure Verification Records',
      desc: 'Immutable audit records anchored with cryptographic SHA-256 hashes and timestamp seals.',
      icon: Lock,
      color: 'slate'
    },
    {
      title: 'Institutional Verification',
      desc: 'Dedicated verification portal for academic institutions, recruiters, and government bodies.',
      icon: Building2,
      color: 'indigo'
    }
  ];

  const steps = [
    {
      step: '01',
      title: 'Upload Document',
      desc: 'Upload academic marksheet, degree certificate, caste or domicile document in PDF or image format.',
      icon: UploadCloud
    },
    {
      step: '02',
      title: 'Verification Process',
      desc: 'Modular verification engine analyzes OCR text, QR authenticity, ELA tampering, stamps, and signatures.',
      icon: Cpu
    },
    {
      step: '03',
      title: 'Get Authentication Result',
      desc: 'Review clear, definitive verification verdict: Authenticated, Suspicious, or Not Authenticated.',
      icon: FileCheck2
    },
    {
      step: '04',
      title: 'Generate Report',
      desc: 'Download official tamper-evident PDF authentication certificate with cryptographic QR seal.',
      icon: FileDown
    }
  ];

  return (
    <div className="space-y-16 pb-16">
      
      {/* 1. HERO SECTION */}
      <section className="relative bg-slate-900 text-white overflow-hidden py-20 lg:py-28 border-b border-slate-800">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-40 pointer-events-none" />
        
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center space-y-6">
          
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-400/30 text-blue-300 text-xs font-semibold">
            <ShieldCheck className="w-4 h-4 text-blue-400" />
            <span>Authentication Validator • Document Integrity</span>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white max-w-3xl mx-auto leading-tight">
            Authentication Validator
          </h1>

          <p className="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Secure Academic Document Verification Platform powered by intelligent multi-layer verification technologies.
          </p>

          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              to={user ? (isStudent ? '/student/verify' : '/college/verification') : '/student/login'}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs sm:text-sm font-semibold shadow-md transition-all cursor-pointer"
            >
              <span>Verify Documents</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            
            <Link
              to="/features"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs sm:text-sm font-semibold transition-all cursor-pointer"
            >
              <span>Explore Platform</span>
            </Link>
          </div>

          {/* Quick trust metrics */}
          <div className="pt-8 grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto border-t border-slate-800/80 text-left">
            <div>
              <p className="text-xl font-bold text-white">12-Check</p>
              <p className="text-xs text-slate-400">Modular Verification</p>
            </div>
            <div>
              <p className="text-xl font-bold text-white">SHA-256</p>
              <p className="text-xs text-slate-400">Cryptographic Hash</p>
            </div>
            <div>
              <p className="text-xl font-bold text-white">OCR + AI</p>
              <p className="text-xs text-slate-400">Intelligent Extraction</p>
            </div>
            <div>
              <p className="text-xl font-bold text-white">100% Secure</p>
              <p className="text-xs text-slate-400">Privacy Preserved</p>
            </div>
          </div>

        </div>
      </section>

      {/* 2. FEATURE CARDS */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <p className="text-xs font-bold uppercase tracking-wider text-blue-600">Verification Capabilities</p>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1">Multi-Layer Authenticity Validation</h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-2">
            Each document undergoes isolated modular inspection across structural, textual, and cryptographic layers.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((f, i) => {
            const Icon = f.icon;
            return (
              <div
                key={i}
                className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs hover:shadow-md transition-shadow relative overflow-hidden flex flex-col justify-between"
              >
                <div>
                  <div className="w-10 h-10 rounded-xl bg-slate-100 text-slate-700 border border-slate-200 flex items-center justify-center mb-4">
                    <Icon className="w-5 h-5 text-slate-800" />
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mb-2">{f.title}</h3>
                  <p className="text-xs text-slate-600 leading-relaxed">{f.desc}</p>
                </div>
                <div className="mt-4 pt-4 border-t border-slate-100 flex items-center text-[11px] font-semibold text-blue-600">
                  <span>Standard Layer Compliant</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 3. HOW IT WORKS */}
      <section className="bg-white border-y border-slate-200 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <p className="text-xs font-bold uppercase tracking-wider text-blue-600">Workflow Process</p>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mt-1">How Document Verification Works</h2>
            <p className="text-xs sm:text-sm text-slate-500 mt-2">
              A frictionless 4-step pipeline designed for academic institutions and students alike.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((s, idx) => {
              const Icon = s.icon;
              return (
                <div key={idx} className="bg-slate-50 rounded-xl border border-slate-200 p-6 relative">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-2xl font-black text-slate-300">{s.step}</span>
                    <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 border border-blue-100 flex items-center justify-center">
                      <Icon className="w-4 h-4" />
                    </div>
                  </div>
                  <h4 className="text-sm font-bold text-slate-900 mb-2">{s.title}</h4>
                  <p className="text-xs text-slate-600 leading-relaxed">{s.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 4. DUAL PORTAL INTRODUCTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Student Portal Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-xs hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-100 text-blue-600 flex items-center justify-center mb-5">
              <UserCheck className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">Student Portal</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-6">
              Empower students to independently upload academic documents, run authenticity checks, connect with authorized colleges, and preserve lifetime verification history.
            </p>
            <ul className="space-y-2 text-xs text-slate-700 mb-8">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Independent document verification without mandatory college link</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Request official linkage with academic institutions via QR/Search</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Download tamper-proof verification reports</span>
              </li>
            </ul>
            <div className="flex gap-3">
              <Link
                to="/student/login"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs"
              >
                <span>Student Login</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <Link
                to="/student/register"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold"
              >
                <span>Register</span>
              </Link>
            </div>
          </div>

          {/* College Portal Card */}
          <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-xs hover:shadow-md transition-shadow">
            <div className="w-12 h-12 rounded-xl bg-slate-100 border border-slate-200 text-slate-800 flex items-center justify-center mb-5">
              <Building2 className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">College & Institute Portal</h3>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed mb-6">
              Institutional console for college administrators to directly verify any candidate document, manage enrolled students, issue college connection QRs, and audit records.
            </p>
            <ul className="space-y-2 text-xs text-slate-700 mb-8">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Direct document verification without requiring student accounts</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Review and approve incoming student link requests</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>Generate institution-branded QR codes and audit logs</span>
              </li>
            </ul>
            <div className="flex gap-3">
              <Link
                to="/college/login"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs"
              >
                <span>College Login</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <Link
                to="/college/register"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold"
              >
                <span>Register College</span>
              </Link>
            </div>
          </div>

        </div>
      </section>

      {/* 5. CALL TO ACTION */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-slate-900 text-white rounded-2xl border border-slate-800 p-8 sm:p-12 text-center relative overflow-hidden">
          <div className="max-w-2xl mx-auto space-y-4 relative z-10">
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
              Ready to Verify Academic Authenticity?
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Start verifying documents directly or explore the verification layers trusted by academic institutions across the country.
            </p>
            <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                to="/student/login"
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs"
              >
                Get Started as Student
              </Link>
              <Link
                to="/college/login"
                className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold"
              >
                Institutional Access
              </Link>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};

export default HomePage;
