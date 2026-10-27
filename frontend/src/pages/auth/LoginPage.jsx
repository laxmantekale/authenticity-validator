import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { ShieldCheck, User, Building2, Lock, Eye, EyeOff, ArrowRight, Loader2, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';

export const LoginPage = () => {
  const [role, setRole] = useState('student'); // 'student' | 'college'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { login } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const handleDemoFill = () => {
    if (role === 'student') {
      setEmail('rahul.patil@student.in');
      setPassword('student123');
    } else {
      setEmail('admin@nit.edu.in');
      setPassword('college123');
    }
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email, password, role);
      toast.success(`Signed in successfully as ${role === 'student' ? 'Student' : 'College'}`);
      const redirectPath = searchParams.get('redirect') || (role === 'student' ? '/student/dashboard' : '/college/dashboard');
      navigate(redirectPath);
    } catch (err) {
      const msg = err.response?.data?.error || 'Invalid credentials. Please verify your email and password.';
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
                <p className="text-xs text-slate-400">Access Portal</p>
              </div>
            </div>

            <div className="space-y-3 pt-4">
              <h3 className="text-xl font-bold text-white leading-snug">
                Secure Academic Document Verification Platform
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Centralized gateway for students and higher educational institutions to verify degree authenticity, marksheets, and academic credentials.
              </p>
            </div>

            <div className="space-y-2 pt-2 text-xs text-slate-300">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Instant multi-layer OCR & cryptographic authenticity check</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Permanent Polygon blockchain verification logs</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Real-time college to student verification handshake</span>
              </div>
            </div>
          </div>

          <div className="pt-8 border-t border-slate-800 text-[11px] text-slate-400 relative z-10 flex items-center justify-between">
            <span>Academic Verification Hub</span>
            <button
              type="button"
              onClick={handleDemoFill}
              className="text-blue-400 hover:text-blue-300 underline font-medium cursor-pointer"
            >
              Demo {role === 'student' ? 'Student' : 'College'} Fill
            </button>
          </div>
        </div>

        {/* Right Side: Auth Form */}
        <div className="p-8 sm:p-10 flex flex-col justify-center">
          <div className="mb-6">
            {/* Role Switcher Tabs */}
            <div className="flex p-1 bg-slate-100 rounded-xl mb-5">
              <button
                type="button"
                onClick={() => { setRole('student'); setError(null); }}
                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-semibold transition-all ${
                  role === 'student'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <User className="w-3.5 h-3.5" />
                <span>Student</span>
              </button>
              <button
                type="button"
                onClick={() => { setRole('college'); setError(null); }}
                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-semibold transition-all ${
                  role === 'college'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Building2 className="w-3.5 h-3.5" />
                <span>Institution</span>
              </button>
            </div>

            <h2 className="text-2xl font-bold tracking-tight text-slate-900">
              {role === 'student' ? 'Student Sign In' : 'Institutional Sign In'}
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              {role === 'student'
                ? 'Enter your student credentials to access your verification dashboard'
                : 'Enter official institution credentials to access verification console'}
            </p>
          </div>

          {error && (
            <div className="mb-5 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs leading-relaxed">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                {role === 'student' ? 'Student Email Address' : 'Official College Email'}
              </label>
              <div className="relative">
                {role === 'student' ? (
                  <User className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                ) : (
                  <Building2 className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                )}
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={role === 'student' ? 'student@example.edu.in' : 'admin@college.edu.in'}
                  className="w-full pl-9 pr-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800 transition-all shadow-xs"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-10 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900/10 focus:border-slate-800 transition-all shadow-xs"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-end">
              <Link
                to="/forgot-password"
                className="text-xs font-medium text-blue-600 hover:text-blue-500 hover:underline"
              >
                Forgot Password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:bg-slate-600"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <span>Sign In as {role === 'student' ? 'Student' : 'College'}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-500">
            <span>Don't have an account?</span>
            <Link
              to={role === 'student' ? '/student/register' : '/college/register'}
              className="font-semibold text-blue-600 hover:text-blue-500"
            >
              {role === 'student' ? 'Register Student' : 'Register Institution'}
            </Link>
          </div>
        </div>

      </div>
    </div>
  );
};

export default LoginPage;
