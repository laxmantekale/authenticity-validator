import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, Menu, X, User, School, QrCode } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import WebsiteQRModal from './WebsiteQRModal';

export const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isQrOpen, setIsQrOpen] = useState(false);
  const location = useLocation();
  const { user, isStudent, isCollege } = useAuth();

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'How It Works', path: '/how-it-works' },
    { name: 'Features', path: '/features' },
    { name: 'About', path: '/about' },
    { name: 'Contact', path: '/contact' }
  ];

  const isActive = (path) => {
    if (path === '/' && location.pathname !== '/') return false;
    return location.pathname.startsWith(path);
  };

  return (
    <>
      <header className="sticky top-0 z-50 bg-slate-900 text-white border-b border-slate-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400 group-hover:bg-blue-600/30 transition-colors shadow-xs">
                <ShieldCheck className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <span className="font-bold text-base tracking-tight text-white block">Authentication Validator</span>
                <p className="text-[11px] text-slate-400 font-medium leading-none mt-0.5">Secure Academic Document Verification Platform</p>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    isActive(link.path)
                      ? 'bg-slate-800 text-blue-400'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  {link.name}
                </Link>
              ))}
            </nav>

            {/* Right Action Buttons */}
            <div className="hidden lg:flex items-center gap-3">
              <button
                onClick={() => setIsQrOpen(true)}
                className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 border border-slate-700/60 transition-colors cursor-pointer"
                title="Platform QR Code"
                aria-label="Platform QR Code"
              >
                <QrCode className="w-4 h-4" />
              </button>

              {user ? (
                <Link
                  to={isStudent ? '/student/dashboard' : isCollege ? '/college/dashboard' : '/'}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-xs font-semibold hover:bg-blue-500 transition-colors shadow-xs"
                >
                  <User className="w-3.5 h-3.5" />
                  <span>Go to Dashboard</span>
                </Link>
              ) : (
                <div className="flex items-center gap-2">
                  <Link
                    to="/student/login"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-slate-200 hover:text-white hover:bg-slate-800 border border-slate-700 text-xs font-semibold transition-colors"
                  >
                    <User className="w-3.5 h-3.5 text-slate-400" />
                    <span>Student Login</span>
                  </Link>
                  <Link
                    to="/college/login"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 text-white text-xs font-semibold hover:bg-blue-500 transition-colors shadow-xs"
                  >
                    <School className="w-3.5 h-3.5" />
                    <span>College Login</span>
                  </Link>
                </div>
              )}
            </div>

            {/* Mobile menu toggle */}
            <div className="flex md:hidden items-center gap-2">
              <button
                onClick={() => setIsQrOpen(true)}
                className="p-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800"
                aria-label="Platform QR Code"
              >
                <QrCode className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(!isOpen)}
                className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                aria-label="Toggle navigation menu"
              >
                {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>

          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {isOpen && (
          <div className="md:hidden border-t border-slate-800 bg-slate-900 px-4 pt-3 pb-5 space-y-3">
            <div className="space-y-1">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setIsOpen(false)}
                  className={`block px-3 py-2 rounded-lg text-xs font-semibold ${
                    isActive(link.path)
                      ? 'bg-slate-800 text-blue-400'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  {link.name}
                </Link>
              ))}
            </div>

            <div className="pt-3 border-t border-slate-800 space-y-2">
              {user ? (
                <Link
                  to={isStudent ? '/student/dashboard' : '/college/dashboard'}
                  onClick={() => setIsOpen(false)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 text-white text-xs font-semibold"
                >
                  <User className="w-4 h-4" />
                  <span>Go to Dashboard</span>
                </Link>
              ) : (
                <>
                  <Link
                    to="/student/login"
                    onClick={() => setIsOpen(false)}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-slate-700 text-slate-200 text-xs font-semibold hover:bg-slate-800"
                  >
                    <User className="w-4 h-4 text-slate-400" />
                    <span>Student Login</span>
                  </Link>
                  <Link
                    to="/college/login"
                    onClick={() => setIsOpen(false)}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 text-white text-xs font-semibold hover:bg-blue-500"
                  >
                    <School className="w-4 h-4" />
                    <span>College Login</span>
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Website QR Modal */}
      <WebsiteQRModal isOpen={isQrOpen} onClose={() => setIsQrOpen(false)} />
    </>
  );
};

export default Navbar;
