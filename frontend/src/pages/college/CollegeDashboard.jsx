import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Building2,
  Users,
  UserCheck,
  ShieldCheck,
  Award,
  UploadCloud,
  ArrowRight,
  Clock,
  CheckCircle2,
  QrCode,
  FolderOpen,
  RefreshCw,
  FileText,
  AlertTriangle
} from 'lucide-react';
import { collegeService } from '../../services/collegeService';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import StatCard from '../../components/common/StatCard';
import SectionCard from '../../components/common/SectionCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import LoadingState from '../../components/common/LoadingState';

export const CollegeDashboard = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboard = async (isManual = false) => {
    try {
      if (isManual) setRefreshing(true);
      else setLoading(true);
      const res = await collegeService.getDashboardStats();
      setData(res.data);
      if (isManual) toast.success('Institutional metrics refreshed');
    } catch (err) {
      toast.error('Unable to retrieve institutional dashboard stats.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return <LoadingState message="Loading institutional console analytics..." />;
  }

  const stats = data?.stats || {};
  const college = data?.college || user || {};
  const recentRequests = data?.recent_requests || [];
  const recentActivity = data?.recent_activity || [];

  return (
    <div className="space-y-6">
      
      <PageHeader
        title={college.college_name || 'Institutional Console'}
        subtitle="Manage enrolled student credentials, link requests, and direct document verifications"
        badge={`Code: ${college.college_id || 'COL'}`}
        action={
          <div className="flex items-center gap-2">
            <button
              onClick={() => fetchDashboard(true)}
              disabled={refreshing}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-60"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            <Link
              to="/college/verification"
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Direct Document Verification</span>
            </Link>
          </div>
        }
      />

      {/* 1. 4 SUMMARY CARDS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Documents"
          value={stats.total_documents ?? 0}
          icon={FileText}
          color="slate"
          subtitle="All repository documents"
        />
        <StatCard
          title="Verified Documents"
          value={stats.verified_documents ?? stats.authenticated_documents ?? stats.authenticated ?? 0}
          icon={ShieldCheck}
          color="emerald"
          subtitle="Authenticated credentials"
        />
        <StatCard
          title="Pending Verification"
          value={stats.pending_not_verified ?? stats.pending_documents ?? stats.pending_verifications ?? 0}
          icon={Clock}
          color="amber"
          subtitle="Awaiting verification analysis"
        />
        <StatCard
          title="Connected Students"
          value={stats.linked_students ?? stats.total_students ?? 0}
          icon={Users}
          color="indigo"
          subtitle="Approved active enrollments"
        />
      </div>

      {/* 2. QUICK ACTIONS & RECENT REQUESTS */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Quick Actions */}
        <SectionCard
          title="Quick Actions"
          subtitle="Direct institutional verification operations"
          className="lg:col-span-1"
        >
          <div className="space-y-2.5">
            <Link
              to="/college/documents"
              className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-blue-300 hover:bg-blue-50/40 transition-all text-xs group"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
                  <UploadCloud className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-bold text-slate-900 group-hover:text-blue-600">Upload Document</p>
                  <p className="text-[11px] text-slate-500">Direct candidate document upload</p>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all" />
            </Link>

            <Link
              to="/college/documents"
              className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-slate-300 hover:bg-slate-50 transition-all text-xs group"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center font-bold">
                  <FolderOpen className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-bold text-slate-900">View Documents</p>
                  <p className="text-[11px] text-slate-500">Direct & linked student documents</p>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-all" />
            </Link>

            <Link
              to="/college/students"
              className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-indigo-300 hover:bg-indigo-50/40 transition-all text-xs group"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
                  <Users className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-bold text-slate-900">View Students</p>
                  <p className="text-[11px] text-slate-500">{stats.linked_students || 0} active student links</p>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-all" />
            </Link>

            <Link
              to="/college/student-requests"
              className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-amber-300 hover:bg-amber-50/40 transition-all text-xs group"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
                  <UserCheck className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-bold text-slate-900">View Requests</p>
                  <p className="text-[11px] text-slate-500">{stats.pending_requests ?? stats.pending_student_requests ?? 0} pending review</p>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-all" />
            </Link>
          </div>
        </SectionCard>

        {/* Pending Requests Stream */}
        <SectionCard
          title="Recent Connection Requests"
          subtitle="Incoming connection requests submitted by students"
          className="lg:col-span-2"
          action={
            <Link
              to="/college/student-requests"
              className="text-xs font-semibold text-blue-600 hover:text-blue-500 flex items-center gap-1"
            >
              <span>Manage Requests</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          }
          noPadding
        >
          {recentRequests.length === 0 ? (
            <div className="p-6">
              <EmptyState
                icon={UserCheck}
                title="No pending student requests"
                message="All incoming student linkage requests have been reviewed."
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50/75 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
                    <th className="px-4 py-3">Student Name</th>
                    <th className="px-4 py-3">Student ID</th>
                    <th className="px-4 py-3">Request Date</th>
                    <th className="px-4 py-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white">
                  {recentRequests.map((req) => (
                    <tr key={req.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-4 py-3.5 font-semibold text-slate-900">
                        {req.student?.full_name || 'Student Candidate'}
                      </td>
                      <td className="px-4 py-3.5 font-mono text-[11px] text-slate-500">
                        {req.student?.student_id || 'STU'}
                      </td>
                      <td className="px-4 py-3.5 text-slate-500">
                        {req.requested_at ? new Date(req.requested_at).toLocaleDateString() : 'Recent'}
                      </td>
                      <td className="px-4 py-3.5">
                        <StatusBadge status={req.status} size="sm" />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </SectionCard>

      </div>

      {/* 3. RECENT DIRECT VERIFICATION ACTIVITY */}
      <SectionCard
        title="Recent Institutional Verifications"
        subtitle="Direct document checks performed by this institution"
        action={
          <Link
            to="/college/history"
            className="text-xs font-semibold text-blue-600 hover:text-blue-500 flex items-center gap-1"
          >
            <span>View Verification History</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        }
        noPadding
      >
        {recentActivity.length === 0 ? (
          <div className="p-6">
            <EmptyState
              icon={ShieldCheck}
              title="No direct verifications recorded"
              message="Upload and verify candidate documents directly to establish an audit log."
              actionLabel="Verify First Document"
              onAction={() => window.location.href = '/college/verification'}
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/75 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="px-4 py-3">Document Title</th>
                  <th className="px-4 py-3">Verification ID</th>
                  <th className="px-4 py-3">Authentication Status</th>
                  <th className="px-4 py-3">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {recentActivity.map((act) => (
                  <tr key={act.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-4 py-3.5 font-semibold text-slate-900">
                      {act.document?.original_filename || act.document?.document_type || 'Academic Record'}
                    </td>
                    <td className="px-4 py-3.5 font-mono text-[11px] text-slate-500">
                      {act.verification_id}
                    </td>
                    <td className="px-4 py-3.5">
                      <StatusBadge status={act.final_status} />
                    </td>
                    <td className="px-4 py-3.5 text-slate-500">
                      {act.verification_date ? new Date(act.verification_date).toLocaleDateString() : 'Recent'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

    </div>
  );
};

export default CollegeDashboard;
