import React, { useState, useEffect, useMemo } from 'react';
import { History, Download, FileText, ShieldCheck, Filter, Loader2, ArrowRight, RefreshCw, Eye, Calendar, Hash, ArrowUpDown } from 'lucide-react';
import { verificationService } from '../../services/verificationService';
import { reportService } from '../../services/reportService';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import DataTable from '../../components/common/DataTable';
import StatusBadge from '../../components/common/StatusBadge';
import SearchInput from '../../components/common/SearchInput';
import LoadingState from '../../components/common/LoadingState';
import Pagination from '../../components/common/Pagination';
import Modal from '../../components/common/Modal';
import ReportViewer from '../../components/reports/ReportViewer';

export const VerificationHistory = () => {
  const { toast } = useToast();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [dateFilter, setDateFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('date_desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [downloadingId, setDownloadingId] = useState(null);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [viewingReportId, setViewingReportId] = useState(null);

  const pageSize = 10;

  const fetchHistory = async (isManual = false) => {
    try {
      if (isManual) setRefreshing(true);
      else setLoading(true);
      const res = await verificationService.getStudentHistory();
      setHistory(res.data.history || []);
      if (isManual) toast.success('Verification history refreshed');
    } catch (err) {
      toast.error('Unable to fetch verification history.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDownloadReport = async (reportId) => {
    if (!reportId) {
      toast.error('Report certificate is not attached to this record.');
      return;
    }

    try {
      setDownloadingId(reportId);
      const res = await reportService.downloadSingleReport(reportId);
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Official PDF report downloaded!');
    } catch (err) {
      toast.error('Failed to download verification report.');
    } finally {
      setDownloadingId(null);
    }
  };

  const filteredAndSorted = useMemo(() => {
    const now = new Date();
    let result = history.filter((h) => {
      const q = search.toLowerCase();
      const matchesSearch =
        (h.document_name || '').toLowerCase().includes(q) ||
        (h.verification_id || '').toLowerCase().includes(q) ||
        (h.report_id || '').toLowerCase().includes(q);

      if (!matchesSearch) return false;

      if (statusFilter !== 'ALL' && (h.authentication_status || '').toUpperCase() !== statusFilter) {
        return false;
      }

      if (dateFilter !== 'ALL' && h.verification_date) {
        const d = new Date(h.verification_date);
        const diffDays = (now - d) / (1000 * 60 * 60 * 24);
        if (dateFilter === '7DAYS' && diffDays > 7) return false;
        if (dateFilter === '30DAYS' && diffDays > 30) return false;
      }

      return true;
    });

    result.sort((a, b) => {
      if (sortBy === 'date_desc') {
        return new Date(b.verification_date || 0) - new Date(a.verification_date || 0);
      }
      if (sortBy === 'date_asc') {
        return new Date(a.verification_date || 0) - new Date(b.verification_date || 0);
      }
      if (sortBy === 'name_asc') {
        return (a.document_name || '').localeCompare(b.document_name || '');
      }
      if (sortBy === 'name_desc') {
        return (b.document_name || '').localeCompare(a.document_name || '');
      }
      return 0;
    });

    return result;
  }, [history, search, statusFilter, sortBy]);

  const totalPages = Math.ceil(filteredAndSorted.length / pageSize) || 1;
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredAndSorted.slice(start, start + pageSize);
  }, [filteredAndSorted, currentPage, pageSize]);

  // Reset page to 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [search, statusFilter, dateFilter, sortBy]);

  const columns = [
    {
      header: 'Document Name',
      key: 'document_name',
      render: (row) => (
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <FileText className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <p className="font-semibold text-slate-900 truncate">{row.document_name || 'Academic Record'}</p>
            <p className="text-[11px] text-slate-400 font-mono truncate">Report: {row.report_id || 'N/A'}</p>
          </div>
        </div>
      )
    },
    {
      header: 'Verification ID',
      key: 'verification_id',
      render: (row) => (
        <span className="font-mono text-xs text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
          {row.verification_id || row.id}
        </span>
      )
    },
    {
      header: 'Status',
      key: 'authentication_status',
      render: (row) => <StatusBadge status={row.authentication_status} />
    },
    {
      header: 'Verification Date',
      key: 'verification_date',
      render: (row) => row.verification_date ? new Date(row.verification_date).toLocaleDateString() : 'Recent'
    },
    {
      header: 'Actions',
      key: 'actions',
      className: 'text-right',
      render: (row) => (
        <div className="flex items-center justify-end gap-1.5">
          {row.report_id ? (
            <button
              type="button"
              onClick={() => setViewingReportId(row.report_id)}
              className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-blue-200 bg-blue-50/50 hover:bg-blue-100/60 text-blue-700 text-xs font-semibold transition-colors cursor-pointer"
              title="View Complete 9-Section Report"
            >
              <Eye className="w-3.5 h-3.5 text-blue-600" />
              <span>View Report</span>
            </button>
          ) : (
            <button
              type="button"
              onClick={() => setSelectedRecord(row)}
              className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition-colors cursor-pointer"
            >
              <Eye className="w-3.5 h-3.5 text-slate-500" />
              <span>Details</span>
            </button>
          )}

          {row.report_id && (
            <button
              onClick={() => handleDownloadReport(row.report_id)}
              disabled={downloadingId === row.report_id}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-40"
              title="Download Official PDF Report"
            >
              {downloadingId === row.report_id ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              <span className="hidden sm:inline">PDF</span>
            </button>
          )}
        </div>
      )
    }
  ];

  if (loading) {
    return <LoadingState message="Loading your verification audit history..." />;
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Verification History"
        subtitle="Permanent audit trail of all authenticity checks performed on your account"
        badge={`${history.length} Records`}
        action={
          <button
            onClick={() => fetchHistory(true)}
            disabled={refreshing}
            className="inline-flex items-center gap-1.5 px-3 py-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-60"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        }
      />

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
          <SearchInput
            value={search}
            onChange={setSearch}
            placeholder="Search by document name, verification ID, or report..."
            className="max-w-md w-full"
          />

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs text-slate-500">
              <Filter className="w-3.5 h-3.5" />
              <span>Status:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              >
                <option value="ALL">All Records</option>
                <option value="AUTHENTICATED">Authenticated</option>
                <option value="NOT_AUTHENTICATED">Not Authenticated</option>
                <option value="SUSPICIOUS">Suspicious</option>
              </select>
            </div>

            <div className="flex items-center gap-1.5 text-xs text-slate-500">
              <Calendar className="w-3.5 h-3.5" />
              <span>Date:</span>
              <select
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              >
                <option value="ALL">All Time</option>
                <option value="7DAYS">Last 7 Days</option>
                <option value="30DAYS">Last 30 Days</option>
              </select>
            </div>

            <div className="flex items-center gap-1.5 text-xs text-slate-500">
              <ArrowUpDown className="w-3.5 h-3.5" />
              <span>Sort:</span>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              >
                <option value="date_desc">Newest First</option>
                <option value="date_asc">Oldest First</option>
                <option value="name_asc">Name (A-Z)</option>
                <option value="name_desc">Name (Z-A)</option>
              </select>
            </div>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={paginatedData}
          emptyTitle="No verification records found"
          emptyMessage="No verification audit records match your current filters."
        />

        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          totalItems={filteredAndSorted.length}
        />
      </div>

      {/* View Result Details Modal */}
      {selectedRecord && (
        <Modal
          isOpen={!!selectedRecord}
          onClose={() => setSelectedRecord(null)}
          title="Verification Result Record"
          maxWidth="max-w-md"
        >
          <div className="space-y-4">
            <div className="text-center p-4 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">
                Audit Result
              </span>
              <div className="my-2 flex justify-center">
                <StatusBadge status={selectedRecord.authentication_status} />
              </div>
              <p className="text-xs font-bold text-slate-900 mt-1">
                {selectedRecord.document_name || 'Academic Document'}
              </p>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Verification ID</span>
                <span className="font-mono font-semibold text-slate-800">{selectedRecord.verification_id || selectedRecord.id}</span>
              </div>
              {selectedRecord.report_id && (
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Report ID</span>
                  <span className="font-mono font-semibold text-blue-600">{selectedRecord.report_id}</span>
                </div>
              )}
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Verification Date</span>
                <span className="text-slate-700">
                  {selectedRecord.verification_date ? new Date(selectedRecord.verification_date).toLocaleString() : 'N/A'}
                </span>
              </div>
              {selectedRecord.sha256_hash && (
                <div className="py-1.5 border-b border-slate-100">
                  <span className="text-slate-500 block text-[11px]">SHA-256 Digest</span>
                  <span className="font-mono text-[11px] text-slate-700 break-all block">
                    {selectedRecord.sha256_hash}
                  </span>
                </div>
              )}
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setSelectedRecord(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
              >
                Close
              </button>
              {selectedRecord.report_id && (
                <>
                  <button
                    type="button"
                    onClick={() => {
                      const rId = selectedRecord.report_id;
                      setSelectedRecord(null);
                      setViewingReportId(rId);
                    }}
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors cursor-pointer"
                  >
                    <Eye className="w-3.5 h-3.5 text-blue-400" />
                    <span>View 9-Section Report</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      handleDownloadReport(selectedRecord.report_id);
                    }}
                    className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-xs transition-colors cursor-pointer"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download PDF</span>
                  </button>
                </>
              )}
            </div>
          </div>
        </Modal>
      )}

      {/* 9-Section Structured Report Viewer Modal */}
      {viewingReportId && (
        <ReportViewer
          reportId={viewingReportId}
          onClose={() => setViewingReportId(null)}
        />
      )}

    </div>
  );
};

export default VerificationHistory;
