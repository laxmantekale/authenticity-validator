import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Lock, Award, CheckCircle2 } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 border-t border-slate-800 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          
          {/* Col 1 & 2: Platform Info */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
                <ShieldCheck className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <span className="font-bold text-sm tracking-tight text-white block">Authentication Validator</span>
                <span className="text-[11px] text-slate-400">Secure Academic Document Verification Platform</span>
              </div>
            </div>
            <p className="text-slate-400 text-xs leading-relaxed max-w-sm">
              Enterprise academic document verification platform powered by multi-signal evidence verification, OCR extraction, tampering analysis, and cryptographic blockchain integrity records.
            </p>
            <div className="flex items-center gap-4 text-[11px] text-slate-400 pt-2">
              <div className="flex items-center gap-1.5">
                <Lock className="w-3.5 h-3.5 text-emerald-400" />
                <span>SHA-256 Anchored</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Award className="w-3.5 h-3.5 text-blue-400" />
                <span>Tamper-Evident</span>
              </div>
            </div>
          </div>

          {/* Col 3: Navigation */}
          <div>
            <h3 className="text-white font-semibold text-xs uppercase tracking-wider mb-3">Platform</h3>
            <ul className="space-y-2 text-xs">
              <li><Link to="/" className="hover:text-white transition-colors">Home</Link></li>
              <li><Link to="/how-it-works" className="hover:text-white transition-colors">How It Works</Link></li>
              <li><Link to="/features" className="hover:text-white transition-colors">Verification Features</Link></li>
              <li><Link to="/about" className="hover:text-white transition-colors">About Platform</Link></li>
              <li><Link to="/contact" className="hover:text-white transition-colors">Contact</Link></li>
            </ul>
          </div>

          {/* Col 4: Portals */}
          <div>
            <h3 className="text-white font-semibold text-xs uppercase tracking-wider mb-3">Portals</h3>
            <ul className="space-y-2 text-xs">
              <li><Link to="/student/login" className="hover:text-white transition-colors">Student Login</Link></li>
              <li><Link to="/student/register" className="hover:text-white transition-colors">Student Registration</Link></li>
              <li><Link to="/college/login" className="hover:text-white transition-colors">College Login</Link></li>
              <li><Link to="/college/register" className="hover:text-white transition-colors">College Registration</Link></li>
            </ul>
          </div>

          {/* Col 5: Security & Compliance */}
          <div>
            <h3 className="text-white font-semibold text-xs uppercase tracking-wider mb-3">Verification Layers</h3>
            <ul className="space-y-1.5 text-[11px] text-slate-400">
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" /> OCR Data Extraction</li>
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" /> QR & Barcode Match</li>
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" /> Multi-Signal Tamper Detection</li>
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" /> Digital Signature & Seal</li>
              <li className="flex items-center gap-1.5"><CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" /> PDF Metadata Analysis</li>
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="mt-10 pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-400">
          <p>© 2026 Authentication Validator</p>
          <div className="flex items-center gap-4">
            <span>Secure TLS Encrypted</span>
            <span>•</span>
            <span>Academic Trust Protocol</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
