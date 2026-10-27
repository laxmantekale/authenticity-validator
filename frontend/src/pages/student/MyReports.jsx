import React, { useState, useEffect, useMemo } from 'react';
import { Award, Download, FileText, ExternalLink, Loader2, RefreshCw, Printer, Eye, Filter, ArrowUpDown, X } from 'lucide-react';
import { reportService } from '../../services/reportService';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import DataTable from '../../components/common/DataTable';
import StatusBadge from '../../components/common/StatusBadge';
import SearchInput from '../../components/common/SearchInput';
import LoadingState from '../../components/common/LoadingState';
import Pagination from '../../components/common/Pagination';
import ReportViewer from '../../components/reports/ReportViewer';

export const MyReports = () => {
  const { toast } = useToast();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('date_desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [downloadingId, setDownloadingId] = useState(null);
  const [downloadingAll, setDownloadingAll] = useState(false);
  const [viewingReport, setViewingReport] = useState(null);

  const pageSize = 10;

  const fetchReports = async (isManual = false) => {
    try {
      if (isManual) setRefreshing(true);
      else setLoading(true);
      const res = await reportService.getMyReports();
      setReports(res.data.reports || []);
      if (isManual) toast.success('Reports list refreshed');
    } catch (err) {
      toast.error('Unable to retrieve authentication reports.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleDownloadSingle = async (reportId) => {
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
      toast.success('Report downloaded successfully!');
    } catch (err) {
      toast.error('Failed to download report.');
    } finally {
      setDownloadingId(null);
    }
  };

  const handleViewReport = (report) => {
    setViewingReport(report);
  };

  const handlePrintReport = async (reportId) => {
    try {
      setDownloadingId(reportId);
      const res = await reportService.downloadSingleReport(reportId);
      const blobUrl = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const printWindow = window.open(blobUrl, '_blank');
      if (printWindow) {
        printWindow.onload = () => printWindow.print();
      } else {
        toast.info('Pop-up blocked. Opened report in new tab.');
      }
    } catch (err) {
      toast.error('Could not prepare report for printing.');
    } finally {
      setDownloadingId(null);
    }
  };

  const handleDownloadCompleteReport = async () => {
    try {
      setDownloadingAll(true);
      const res = await reportService.downloadCompleteStudentReport();
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Complete_Academic_Authentication_Dossier.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Complete student authentication dossier downloaded!');
    } catch (err) {
      toast.error('Failed to download complete dossier.');
    } finally {
      setDownloadingAll(false);
    }
  };

  const filteredAndSorted = useMemo(() => {
    let result = reports.filter((r) => {
      const q = search.toLowerCase();
      const matchesSearch =
        (r.document_name || '').toLowerCase().includes(q) ||
        (r.report_id || '').toLowerCase().includes(q);

      if (statusFilter === 'ALL') return matchesSearch;
      return matchesSearch && (r.authentication_status || '').toUpperCase() === statusFilter;
    });

    result.sort((a, b) => {
      if (sortBy === 'date_desc') {
        return new Date(b.generated_at || 0) - new Date(a.generated_at || 0);
      }
      if (sortBy === 'date_asc') {
        return new Date(a.generated_at || 0) - new Date(b.generated_at || 0);
      }
      if (sortBy === 'name_asc') {
        return (a.document_name || '').localeCompare(b.document_name || '');
      }
      if (sortBy === 'id_asc') {
        return (a.report_id || '').localeCompare(b.report_id || '');
      }
      return 0;
    });

    return result;
  }, [reports, search, statusFilter, sortBy]);

  const totalPages = Math.ceil(filteredAndSorted.length / pageSize) || 1;
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredAndSorted.slice(start, start + pageSize);
  }, [filteredAndSorted, currentPage, pageSize]);

  useEffect(() => {
    setCurrentPage(1);
  }, [search, statusFilter, sortBy]);

  const columns = [
    {
      header: 'Report ID',
      key: 'report_id',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Award className="w-4 h-4 text-blue-600 shrink-0" />
          <span className="font-mono font-bold text-slate-900 text-xs">{row.report_id}</span>
        </div>
      )
    },
    {
      header: 'Verified Document',
      key: 'document_name',
      render: (row) => <span className="font-semibold text-slate-900">{row.document_name || 'Academic Record'}</span>
    },
    {
      header: 'Authentication Verdict',
      key: 'authentication_status',
      render: (row) => <StatusBadge status={row.authentication_status} />
    },
    {
      header: 'Generated Date',
      key: 'generated_at',
      render: (row) => row.generated_at ? new Date(row.generated_at).toLocaleDateString() : 'Recent'
    },
    {
      header: 'Actions',
      key: 'actions',
      className: 'text-right',
      render: (row) => (
        <div className="flex items-center justify-end gap-1.5">
          <button
            type="button"
            onClick={() => handleViewReport(row)}
            disabled={downloadingId === row.report_id}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition-colors cursor-pointer"
            title="View PDF"
          >
            <Eye className="w-3.5 h-3.5 text-slate-600" />
            <span className="hidden sm:inline">View</span>
          </button>

          <button
            type="button"
            onClick={() => handlePrintReport(row.report_id)}
            disabled={downloadingId === row.report_id}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition-colors cursor-pointer"
            title="Print Report"
          >
            <Printer className="w-3.5 h-3.5 text-slate-600" />
            <span className="hidden sm:inline">Print</span>
          </button>

          <button
            type="button"
            onClick={() => handleDownloadSingle(row.report_id)}
            disabled={downloadingId === row.report_id}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-40"
            title="Download PDF Certificate"
          >
            {downloadingId === row.report_id ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Download className="w-3.5 h-3.5" />
            )}
            <span className="hidden md:inline">Download</span>
          </button>
        </div>
      )
    }
  ];

  if (loading) {
    return <LoadingState message="Loading your official authentication reports..." />;
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Authentication Reports"
        subtitle="Official certificates of verification and comprehensive academic authentication dossiers"
        badge={`${reports.length} Reports`}
        action={
          <div className="flex items-center gap-2">
            <button
              onClick={() => fetchReports(true)}
              disabled={refreshing}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-60"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            {reports.length > 0 && (
              <button
                onClick={handleDownloadCompleteReport}
                disabled={downloadingAll}
                className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-60"
              >
                {downloadingAll ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Download className="w-4 h-4" />
                )}
                <span>Download Complete Dossier</span>
              </button>
            )}
          </div>
        }
      />

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
          <SearchInput
            value={search}
            onChange={setSearch}
            placeholder="Search reports by Report ID or document name..."
            className="max-w-md w-full"
          />

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs text-slate-500">
              <Filter className="w-3.5 h-3.5" />
              <span>Verdict:</span>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
              >
                <option value="ALL">All Reports</option>
                <option value="AUTHENTICATED">Authenticated</option>
                <option value="NOT_AUTHENTICATED">Not Authenticated</option>
                <option value="SUSPICIOUS">Suspicious</option>
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
                <option value="name_asc">Document Name (A-Z)</option>
                <option value="id_asc">Report ID</option>
              </select>
            </div>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={paginatedData}
          emptyTitle="No reports generated yet"
          emptyMessage="Verify a document to generate an official authentication certificate."
        />

        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
          totalItems={filteredAndSorted.length}
        />
      </div>

      {/* Structured Verification Report Modal */}
      {viewingReport && (
        <ReportViewer
          reportId={viewingReport.report_id}
          onClose={() => setViewingReport(null)}
        />
      )}

    </div>
  );
};

export default MyReports;
