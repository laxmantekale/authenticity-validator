import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { Building2, ShieldCheck, Mail, MapPin, CheckCircle, ArrowRight, Loader2 } from 'lucide-react';
import api from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';

export const CollegeConnectPage = () => {
  const { identifier } = useParams();
  const [college, setCollege] = useState(null);
  const [loading, setLoading] = useState(true);
  const [requesting, setRequesting] = useState(false);
  const [requested, setRequested] = useState(false);
  const { user, isStudent } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCollege = async () => {
      try {
        setLoading(true);
        const res = await api.get(`/college/public-info/${identifier}`);
        setCollege(res.data.college);
      } catch (err) {
        toast.error('Unable to locate the specified college.');
      } finally {
        setLoading(false);
      }
    };

    if (identifier) {
      fetchCollege();
    }
  }, [identifier]);

  const handleConnect = async () => {
    if (!user) {
      navigate(`/student/login?redirect=/college-connect/${identifier}`);
      return;
    }

    try {
      setRequesting(true);
      await api.post('/student/colleges/request-link', {
        college_id: college.id,
        secure_link_token: identifier
      });
      setRequested(true);
      toast.success(`Connection request sent to ${college.college_name}!`);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to submit link request.');
    } finally {
      setRequesting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-slate-700 animate-spin" />
      </div>
    );
  }

  if (!college) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center space-y-4">
        <Building2 className="w-12 h-12 text-slate-400 mx-auto" />
        <h2 className="text-lg font-bold text-slate-900">Institution Not Found</h2>
        <p className="text-xs text-slate-500">The QR link or invitation code appears to be expired or invalid.</p>
        <Link to="/" className="inline-block px-4 py-2 rounded-lg bg-slate-900 text-white text-xs font-semibold">
          Return to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8">
      
      <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm text-center space-y-6">
        <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200 text-blue-600 flex items-center justify-center font-bold text-2xl mx-auto">
          {college.college_name.charAt(0)}
        </div>

        <div>
          <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            Verified Academic Institution
          </span>
          <h1 className="text-2xl font-bold text-slate-900 mt-2">{college.college_name}</h1>
          <p className="text-xs text-slate-500 font-mono mt-1">Code: {college.college_id}</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs text-slate-600 text-left bg-slate-50 p-4 rounded-xl border border-slate-200/80 max-w-lg mx-auto">
          <div className="flex items-center gap-2">
            <Mail className="w-4 h-4 text-slate-400 shrink-0" />
            <span className="truncate">{college.official_email}</span>
          </div>
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-slate-400 shrink-0" />
            <span className="truncate">{college.address || 'Campus Address Registered'}</span>
          </div>
        </div>

        {requested ? (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl text-xs flex items-center justify-center gap-2 max-w-md mx-auto">
            <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>Connection request is pending approval by {college.college_name}.</span>
          </div>
        ) : (
          <div className="max-w-md mx-auto space-y-3 pt-2">
            <p className="text-xs text-slate-600">
              Connecting allows {college.college_name} to verify your academic documents directly through their institutional portal.
            </p>

            {user && isStudent ? (
              <button
                onClick={handleConnect}
                disabled={requesting}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:bg-blue-400"
              >
                {requesting ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <span>Send Connection Request</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            ) : (
              <div className="flex flex-col sm:flex-row gap-3">
                <Link
                  to={`/student/login?redirect=/college-connect/${identifier}`}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 text-white text-xs font-semibold hover:bg-blue-500 shadow-xs"
                >
                  <span>Student Login to Connect</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  to={`/student/register?redirect=/college-connect/${identifier}`}
                  className="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 text-xs font-semibold hover:bg-slate-50"
                >
                  Register
                </Link>
              </div>
            )}
          </div>
        )}

      </div>

    </div>
  );
};

export default CollegeConnectPage;
