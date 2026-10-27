import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Printer,
  Users,
  Search,
  CheckCircle2,
  AlertCircle,
  Phone,
  FileCheck,
  Eye,
  ShieldCheck,
  Building2,
  FileSpreadsheet,
  RefreshCw
} from 'lucide-react';
import api from '../../services/api';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import SectionCard from '../../components/common/SectionCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import LoadingState from '../../components/common/LoadingState';
import SearchInput from '../../components/common/SearchInput';
import ConfirmationModal from '../../components/common/ConfirmationModal';
import ReportViewer from '../../components/reports/ReportViewer';

export const CollegeReports = () => {
  const { toast } = useToast();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [downloadingId, setDownloadingId] = useState(null);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [studentDocs, setStudentDocs] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [viewingReportId, setViewingReportId] = useState(null);

  const [refreshing, setRefreshing] = useState(false);

  const fetchStudentsWithReports = async (isManual = false) => {
    try {
      if (isManual) setRefreshing(true);
      else setLoading(true);
      const res = await api.get('/college/students');
      setStudents(res.data.students || []);
      if (isManual) toast.success('Reports list refreshed');
    } catch (err) {
      console.error('Failed to load students for reports', err);
      toast.error('Unable to load institutional student reports.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStudentsWithReports();
  }, []);

  const handleDownloadStudentReport = async (student) => {
    setDownloadingId(student.id);
    try {
      const res = await api.get(`/reports/student/${student.id}/download-complete`, {
        responseType: 'blob'
      });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Complete_Authentication_Report_${student.student_id_code || student.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success(`Complete Authentication Report for ${student.full_name} downloaded successfully.`);
    } catch (err) {
      console.error('Download failed', err);
      toast.error(err.response?.data?.error || `No authenticated documents available for ${student.full_name}.`);
    } finally {
      setDownloadingId(null);
    }
  };

  const handleOpenStudentDocs = async (student) => {
    setSelectedStudent(student);
    setLoadingDocs(true);
    try {
      const res = await api.get(`/college/student/${student.id}/documents`);
      setStudentDocs(res.data.documents || []);
    } catch (err) {
      console.error('Failed to load student documents', err);
      setStudentDocs(student.documents || []);
    } finally {
      setLoadingDocs(false);
    }
  };

  const handleViewDocument = (docId) => {
    window.open(`/api/documents/${docId}/view`, '_blank');
  };

  const handleViewReport = (reportId) => {
    if (!reportId) return;
    setViewingReportId(reportId);
  };

  const filtered = students.filter(s => {
    const name = (s.full_name || '').toLowerCase();
    const code = (s.student_id_code || '').toLowerCase();
    const query = search.toLowerCase();
    return name.includes(query) || code.includes(query);
  });

  if (loading) {
    return <LoadingState message="Loading institutional reports & dossiers..." />;
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Institutional Reports & Audit Dossiers"
        subtitle="Generate comprehensive PDF audit packages for enrolled candidates and inspect individual verification certificates"
        badge={`${students.length} Enrolled Students`}
        action={
          <button
            onClick={() => fetchStudentsWithReports(true)}
            disabled={refreshing}
            className="inline-flex items-center gap-1.5 px-3 py-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-60"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        }
      />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Search by student name or Roll/ID..."
          className="max-w-md w-full"
        />
        <div className="text-xs text-slate-500">
          Showing {filtered.length} of {students.length} candidates
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={FileSpreadsheet}
          title="No Student Records Found"
          message={
            search
              ? 'No enrolled students match your search criteria.'
              : 'Enrolled students and their verified credentials will appear here once linked.'
          }
        />
      ) : (
        <div className="space-y-3">
          {filtered.map((s) => {
            const verifiedDocs = (s.documents || []).filter(
              d => d.latest_status === 'AUTHENTICATED' || d.latest_status === 'Authenticated' || d.verification_status === 'AUTHENTICATED' || d.verification_status === 'Authenticated'
            );
            const isDownloading = downloadingId === s.id;

            return (
              <div
                key={s.id}
                className="bg-white rounded-xl border border-slate-200 p-4 sm:p-5 shadow-xs hover:border-slate-300 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                {/* Student Info */}
                <div className="flex items-start sm:items-center gap-3.5">
                  <div className="w-11 h-11 rounded-xl bg-blue-50 text-blue-700 font-bold flex items-center justify-center shrink-0 border border-blue-200">
                    <Users className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-sm sm:text-base font-bold text-slate-900">{s.full_name}</h3>
                      <span className="text-[11px] font-mono font-bold px-2 py-0.5 bg-slate-100 text-slate-700 rounded border border-slate-200">
                        {s.student_id_code}
                      </span>
                      {verifiedDocs.length > 0 ? (
                        <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 text-[11px] font-semibold rounded border border-emerald-200">
                          {verifiedDocs.length} Authenticated
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 bg-slate-100 text-slate-500 text-[11px] font-medium rounded">
                          0 Verified
                        </span>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                      {s.mobile_number && (
                        <span className="flex items-center gap-1">
                          <Phone className="w-3.5 h-3.5 text-slate-400" /> {s.mobile_number}
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <FileCheck className="w-3.5 h-3.5 text-blue-600" />
                        <span className="font-semibold text-slate-700">{s.total_documents || (s.documents ? s.documents.length : 0)}</span> Total Documents
                      </span>
                    </div>
                  </div>
                </div>

                {/* Right Side Actions */}
                <div className="flex flex-wrap items-center gap-2 self-stretch md:self-auto">
                  <button
                    onClick={() => handleOpenStudentDocs(s)}
                    className="flex-1 md:flex-none inline-flex items-center justify-center gap-1.5 px-3.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg text-xs transition-colors"
                  >
                    <Eye className="w-3.5 h-3.5" />
                    <span>View Documents</span>
                  </button>

                  <button
                    onClick={() => handleDownloadStudentReport(s)}
                    disabled={isDownloading}
                    className="flex-1 md:flex-none inline-flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg text-xs transition-colors shadow-xs disabled:opacity-50"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>{isDownloading ? 'Generating...' : 'Download Dossier'}</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Student Documents Modal */}
      {selectedStudent && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl border border-slate-200 max-w-2xl w-full p-6 shadow-xl space-y-4 max-h-[85vh] flex flex-col">
            <div className="flex items-start justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="font-bold text-slate-900 text-base sm:text-lg">
                  Institutional Dossier: {selectedStudent.full_name}
                </h3>
                <p className="text-xs text-slate-500 font-mono">
                  Roll / ID: {selectedStudent.student_id_code}
                </p>
              </div>
              <button
                onClick={() => {
                  setSelectedStudent(null);
                  setStudentDocs([]);
                }}
                className="text-slate-400 hover:text-slate-600 text-sm font-semibold p-1"
              >
                ✕
              </button>
            </div>

            <div className="overflow-y-auto space-y-3 pr-1 flex-1">
              {loadingDocs ? (
                <LoadingState message="Loading documents..." />
              ) : studentDocs.length === 0 ? (
                <EmptyState
                  icon={FileText}
                  title="No documents submitted"
                  message="This candidate has not uploaded academic credentials yet."
                />
              ) : (
                studentDocs.map((doc) => {
                  const docDisplayName = doc.display_name || doc.name || doc.document_type || 'Academic Document';
                  const reportCode = doc.report_id || doc.report_id_code;

                  return (
                    <div
                      key={doc.id}
                      className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-100/60 transition-colors"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <h4 className="text-xs sm:text-sm font-bold text-slate-900">{docDisplayName}</h4>
                          <StatusBadge status={doc.verification_status || doc.latest_status} />
                        </div>
                        <p className="text-[11px] text-slate-500 font-mono">
                          Classification: {doc.document_type} {doc.uploaded_at && `• ${new Date(doc.uploaded_at).toLocaleDateString()}`}
                        </p>
                        {reportCode && (
                          <p className="text-[11px] text-blue-700 font-mono">
                            Report ID: {reportCode}
                          </p>
                        )}
                      </div>

                      <div className="flex items-center gap-2 self-start sm:self-center">
                        <button
                          onClick={() => handleViewDocument(doc.id)}
                          className="inline-flex items-center gap-1 px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold shadow-xs transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View Doc</span>
                        </button>

                        {reportCode && (
                          <button
                            onClick={() => handleViewReport(reportCode)}
                            className="inline-flex items-center gap-1 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors"
                          >
                            <Printer className="w-3.5 h-3.5" />
                            <span>Certificate</span>
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => {
                  setSelectedStudent(null);
                  setStudentDocs([]);
                }}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-lg text-xs transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Structured Verification Report Modal */}
      {viewingReportId && (
        <ReportViewer
          reportId={viewingReportId}
          onClose={() => setViewingReportId(null)}
        />
      )}
    </div>
  );
};

export default CollegeReports;
