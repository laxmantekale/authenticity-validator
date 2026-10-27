import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  ShieldCheck,
  Clock,
  Award,
  Building2,
  ArrowRight,
  UploadCloud,
  CheckCircle,
  AlertTriangle,
  FileSearch,
  ExternalLink,
  RefreshCw,
  Eye,
  XCircle,
  Hash,
  Calendar
} from 'lucide-react';
import { studentService } from '../../services/studentService';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import StatCard from '../../components/common/StatCard';
import SectionCard from '../../components/common/SectionCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import LoadingState from '../../components/common/LoadingState';
import Modal from '../../components/common/Modal';

export const StudentDashboard = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);

  const fetchDashboard = async (isManual = false) => {
    try {
      if (isManual) setRefreshing(true);
      else setLoading(true);
      const res = await studentService.getDashboardStats();
      setData(res.data);
      if (isManual) toast.success('Dashboard metrics refreshed');
    } catch (err) {
      toast.error('Unable to retrieve dashboard metrics.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  if (loading) {
    return <LoadingState message="Loading student dashboard metrics..." />;
  }

  const stats = data?.stats || {};
  const student = data?.student || user || {};
  const recentVerifications = data?.recent_verifications || [];

  return (
    <div className="space-y-6">
      
      {/* Page Header */}
      <PageHeader
        title={`Welcome back, ${student.full_name || 'Student'}`}
        subtitle="Manage your academic credentials and document verification activity."
        badge={`ID: ${student.student_id || 'STU'}`}
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
              to="/student/verify"
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Verify New Document</span>
            </Link>
          </div>
        }
      />

      {/* 1. STATS METRICS GRID */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Documents"
          value={stats.total_documents ?? 0}
          icon={FileText}
          color="slate"
          subtitle="Active uploaded documents"
        />
        <StatCard
          title="Verified Documents"
          value={stats.verified_documents ?? stats.authenticated_documents ?? stats.authenticated ?? 0}
          icon={ShieldCheck}
          color="emerald"
          subtitle="Passed all authenticity checks"
        />
        <StatCard
          title="Pending / Not Verified"
          value={stats.pending_not_verified ?? ((stats.pending || 0) + (stats.not_verified || 0))}
          icon={AlertTriangle}
          color="amber"
          subtitle={`${stats.pending || 0} pending, ${stats.not_verified || 0} unverified`}
        />
        <StatCard
          title="Verification History"
          value={stats.total_history ?? stats.total_verifications ?? 0}
          icon={Clock}
          color="blue"
          subtitle="Total recorded audit events"
        />
      </div>

      {/* 2. QUICK ACTIONS & RECENT ACTIVITY */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Quick Actions Card */}
        <SectionCard
          title="Quick Actions"
          subtitle="Direct workflows for credential management"
          className="lg:col-span-1"
        >
          <div className="space-y-2.5">
            <Link
              to="/student/verify"
              className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-blue-300 hover:bg-blue-50/40 transition-all text-xs group"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
                  <UploadCloud className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-bold text-slate-900 group-hover:text-blue-600">Verify Document</p>
                  <p className="text-[11px] text-slate-500">Run automatic authenticity check</p>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all" />
            </Link>

            <Link
              to="/student/history"
              className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-slate-300 hover:bg-slate-50 transition-all text-xs group"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center font-bold">
                  <Clock className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-bold text-slate-900">View History</p>
                  <p className="text-[11px] text-slate-500">Past verification audits & logs</p>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-all" />
            </Link>

            <Link
              to="/student/reports"
              className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-slate-300 hover:bg-slate-50 transition-all text-xs group"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
                  <FileSearch className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-bold text-slate-900">View Reports</p>
                  <p className="text-[11px] text-slate-500">Official cryptographic PDF reports</p>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-all" />
            </Link>

            <Link
              to="/student/colleges"
              className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:border-slate-300 hover:bg-slate-50 transition-all text-xs group"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
                  <Building2 className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-bold text-slate-900">College Connections</p>
                  <p className="text-[11px] text-slate-500">{stats.linked_colleges || 0} active institutional links</p>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-all" />
            </Link>
          </div>
        </SectionCard>

        {/* Recent Verification Activity */}
        <SectionCard
          title="Recent Verification Activity"
          subtitle="Latest document validations performed on your account"
          className="lg:col-span-2"
          action={
            <Link
              to="/student/history"
              className="text-xs font-semibold text-blue-600 hover:text-blue-500 flex items-center gap-1"
            >
              <span>View All History</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          }
          noPadding
        >
          {recentVerifications.length === 0 ? (
            <div className="p-6">
              <EmptyState
                title="No recent verifications"
                message="You haven't verified any documents yet. Upload a document to test the authenticity pipeline."
                actionLabel="Start First Verification"
                onAction={() => window.location.href = '/student/verify'}
              />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50/75 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
                    <th className="px-4 py-3">Document Title</th>
                    <th className="px-4 py-3">Verification ID</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Date</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white">
                  {recentVerifications.map((v) => (
                    <tr key={v.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-4 py-3.5 font-semibold text-slate-900">
                        {v.document?.original_filename || v.document?.document_type || 'Academic Record'}
                      </td>
                      <td className="px-4 py-3.5 font-mono text-[11px] text-slate-500">
                        {v.verification_id}
                      </td>
                      <td className="px-4 py-3.5">
                        <StatusBadge status={v.final_status} />
                      </td>
                      <td className="px-4 py-3.5 text-slate-500">
                        {v.verification_date ? new Date(v.verification_date).toLocaleDateString() : 'Recent'}
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <button
                          type="button"
                          onClick={() => setSelectedResult(v)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors cursor-pointer"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View Result</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </SectionCard>

      </div>

      {/* Verification Result Details Modal */}
      {selectedResult && (
        <Modal
          isOpen={!!selectedResult}
          onClose={() => setSelectedResult(null)}
          title="Verification Result Summary"
          maxWidth="max-w-md"
        >
          <div className="space-y-4">
            <div className="text-center p-4 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                Official Result
              </span>
              <div className="my-2 flex justify-center">
                <StatusBadge status={selectedResult.final_status} />
              </div>
              <p className="text-xs font-bold text-slate-900 mt-1">
                {selectedResult.document?.original_filename || selectedResult.document?.document_type || 'Academic Document'}
              </p>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Verification ID</span>
                <span className="font-mono font-semibold text-slate-800">{selectedResult.verification_id}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Document Type</span>
                <span className="font-semibold text-slate-800">{selectedResult.document?.document_type || 'Academic Document'}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Date</span>
                <span className="text-slate-700">
                  {selectedResult.verification_date ? new Date(selectedResult.verification_date).toLocaleString() : 'N/A'}
                </span>
              </div>
              {selectedResult.confidence_score !== undefined && selectedResult.confidence_score !== null && (
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Confidence</span>
                  <span className="font-semibold text-slate-800">{selectedResult.confidence_score}%</span>
                </div>
              )}
              {selectedResult.qr_verified !== undefined && (
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">QR Code Verification</span>
                  <span className={selectedResult.qr_verified ? "text-emerald-600 font-semibold" : "text-slate-500"}>
                    {selectedResult.qr_verified ? "Verified ✓" : "Not Present / N/A"}
                  </span>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setSelectedResult(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
              >
                Close
              </button>
              <Link
                to="/student/history"
                className="inline-flex items-center gap-1 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors"
              >
                <span>Full History</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </Modal>
      )}

    </div>
  );
};

export default StudentDashboard;
