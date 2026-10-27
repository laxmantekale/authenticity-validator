import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Mail, ArrowLeft, ArrowRight, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { authService } from '../../services/authService';
import { useToast } from '../../context/ToastContext';

export const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState(null);
  const { toast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      setError('Please enter your registered email address');
      return;
    }

    // Basic email regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError('Please enter a valid email address');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      await authService.forgotPassword(email.trim().toLowerCase());
      setSubmitted(true);
      toast.success('Password reset instructions sent');
    } catch (err) {
      // Even on error, show generic message or safe error
      const msg = err.response?.data?.error || 'Unable to process reset request. Please check your connection and try again.';
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="max-w-4xl w-full bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden grid grid-cols-1 md:grid-cols-2">
        
        {/* Left Side: Branding & Info */}
        <div className="bg-slate-900 text-white p-8 sm:p-10 flex flex-col justify-between relative overflow-hidden">
          <div className="space-y-6 relative z-10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
                <ShieldCheck className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white leading-tight">Authentication Validator</h2>
                <p className="text-xs text-slate-400">Account Recovery</p>
              </div>
            </div>

            <div className="space-y-3 pt-4">
              <h3 className="text-xl font-bold text-white leading-snug">
                Secure Academic Document Verification Platform
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Reset your password securely. We maintain bank-grade cryptographic hashing and tokenized single-use links to keep your academic credentials safe.
              </p>
            </div>

            <div className="space-y-2 pt-2 text-xs text-slate-300">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Encrypted single-use reset links (valid for 1 hour)</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Works for both Student and Institutional accounts</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Zero exposure of account existence status</span>
              </div>
            </div>
          </div>

          <div className="pt-8 border-t border-slate-800 text-[11px] text-slate-400 relative z-10 flex items-center justify-between">
            <span>Authentication Validator Security</span>
            <Link to="/student/login" className="text-blue-400 hover:text-blue-300 font-medium">
              Back to Login
            </Link>
          </div>
        </div>

        {/* Right Side: Form / Success */}
        <div className="p-8 sm:p-10 flex flex-col justify-center">
          {!submitted ? (
            <>
              <div className="mb-6">
                <Link to="/student/login" className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-slate-800 mb-4 transition-colors">
                  <ArrowLeft className="w-3.5 h-3.5" />
                  <span>Back to Sign In</span>
                </Link>
                <h2 className="text-2xl font-bold tracking-tight text-slate-900">Forgot Password?</h2>
                <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                  Enter the email address registered with your Student or College account. We will send you instructions to safely reset your password.
                </p>
              </div>

              {error && (
                <div className="mb-5 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">Registered Email Address</label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value);
                        if (error) setError(null);
                      }}
                      placeholder="name@example.com"
                      className="w-full pl-9 pr-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800 transition-all shadow-xs"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:bg-slate-600"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Sending instructions...</span>
                    </>
                  ) : (
                    <>
                      <span>Send Reset Instructions</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>

              <div className="mt-8 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span>Remember your password?</span>
                <Link to="/student/login" className="font-semibold text-blue-600 hover:text-blue-500">
                  Student Login
                </Link>
              </div>
            </>
          ) : (
            <div className="text-center py-4 space-y-4">
              <div className="w-14 h-14 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-2 shadow-xs">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h2 className="text-xl font-bold text-slate-900">Check Your Email</h2>
              <p className="text-xs text-slate-600 leading-relaxed max-w-sm mx-auto">
                If an account exists for <span className="font-semibold text-slate-900">{email}</span>, we have sent instructions to reset your password. The link will expire in 1 hour.
              </p>
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-[11px] text-slate-500 max-w-sm mx-auto text-left space-y-1">
                <p className="font-medium text-slate-700">Didn't receive the email?</p>
                <ul className="list-disc list-inside space-y-0.5">
                  <li>Check your spam or junk folder</li>
                  <li>Verify that you entered the registered email correctly</li>
                </ul>
              </div>
              <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
                <button
                  type="button"
                  onClick={() => setSubmitted(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                >
                  Try another email
                </button>
                <Link
                  to="/student/login"
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-colors"
                >
                  Return to Sign In
                </Link>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default ForgotPassword;
