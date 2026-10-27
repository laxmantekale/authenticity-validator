import React, { useState, useEffect } from 'react';
import { UserCheck, Check, X, Search, Clock, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { collegeService } from '../../services/collegeService';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import DataTable from '../../components/common/DataTable';
import StatusBadge from '../../components/common/StatusBadge';
import SearchInput from '../../components/common/SearchInput';
import ConfirmationModal from '../../components/common/ConfirmationModal';
import LoadingState from '../../components/common/LoadingState';

export const StudentRequests = () => {
  const { toast } = useToast();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  // Confirmation Modal State
  const [modalState, setModalState] = useState({
    isOpen: false,
    req: null,
    action: null,
    loading: false
  });

  const fetchRequests = async () => {
    try {
      setLoading(true);
      const res = await collegeService.getStudentRequests(statusFilter === 'ALL' ? undefined : statusFilter);
      setRequests(res.data.requests || []);
    } catch (err) {
      toast.error('Unable to fetch student connection requests.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, [statusFilter]);

  const handleActionClick = (req, action) => {
    setModalState({
      isOpen: true,
      req,
      action,
      loading: false
    });
  };

  const handleConfirmAction = async () => {
    const { req, action } = modalState;
    if (!req || !action) return;

    try {
      setModalState((prev) => ({ ...prev, loading: true }));
      if (action === 'accept') {
        await collegeService.acceptStudentRequest(req.id);
        toast.success(`Accepted linkage for ${req.student?.full_name || 'student'}.`);
      } else {
        await collegeService.rejectStudentRequest(req.id);
        toast.info(`Rejected request from ${req.student?.full_name || 'student'}.`);
      }
      setModalState({ isOpen: false, req: null, action: null, loading: false });
      fetchRequests();
    } catch (err) {
      toast.error(err.response?.data?.error || `Failed to ${action} request.`);
      setModalState((prev) => ({ ...prev, loading: false }));
    }
  };

  const filtered = requests.filter((r) => {
    const q = search.toLowerCase();
    return (
      r.student?.full_name?.toLowerCase().includes(q) ||
      r.student?.email?.toLowerCase().includes(q) ||
      r.student?.student_id?.toLowerCase().includes(q)
    );
  });

  const columns = [
    {
      header: 'Student Candidate',
      key: 'student',
      render: (row) => (
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-blue-50 text-blue-700 flex items-center justify-center font-bold text-xs shrink-0">
            {row.student?.full_name ? row.student.full_name.charAt(0) : 'S'}
          </div>
          <div>
            <p className="font-semibold text-slate-900">{row.student?.full_name || 'Candidate'}</p>
            <p className="text-[11px] text-slate-400">{row.student?.email}</p>
          </div>
        </div>
      )
    },
    {
      header: 'Student ID',
      key: 'student_id_code',
      render: (row) => (
        <span className="font-mono text-xs font-semibold text-slate-800 bg-slate-100 px-2 py-0.5 rounded">
          {row.student?.student_id || 'STU'}
        </span>
      )
    },
    {
      header: 'Request Date',
      key: 'requested_at',
      render: (row) => row.requested_at ? new Date(row.requested_at).toLocaleDateString() : 'Recent'
    },
    {
      header: 'Status',
      key: 'status',
      render: (row) => <StatusBadge status={row.status} />
    },
    {
      header: 'Actions',
      key: 'actions',
      className: 'text-right',
      render: (row) => {
        const isPending = row.status?.toUpperCase() === 'PENDING';
        if (!isPending) {
          return (
            <span className="text-xs text-slate-400 font-medium">
              {row.status?.toUpperCase() === 'ACCEPTED' ? 'Linked' : 'Declined'}
            </span>
          );
        }

        return (
          <div className="flex items-center justify-end gap-2">
            <button
              onClick={() => handleActionClick(row, 'accept')}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <Check className="w-3.5 h-3.5" />
              <span>Accept</span>
            </button>
            <button
              onClick={() => handleActionClick(row, 'reject')}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-rose-200 text-rose-600 hover:bg-rose-50 text-xs font-semibold transition-colors cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
              <span>Reject</span>
            </button>
          </div>
        );
      }
    }
  ];

  if (loading && requests.length === 0) {
    return <LoadingState message="Loading student link requests..." />;
  }

  const pendingCount = requests.filter((r) => r.status?.toUpperCase() === 'PENDING').length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Student Connection Requests"
        subtitle="Review and approve student linkage requests to authorize institutional verification access"
        badge={`${pendingCount} Pending Review`}
      />

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
          <SearchInput
            value={search}
            onChange={setSearch}
            placeholder="Search by student name, ID, or email..."
            className="max-w-md w-full"
          />

          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-500">Filter:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
            >
              <option value="ALL">All Requests</option>
              <option value="PENDING">Pending Only</option>
              <option value="ACCEPTED">Accepted</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={filtered}
          emptyTitle="No connection requests found"
          emptyMessage="There are currently no incoming student connection requests matching your criteria."
        />
      </div>

      {/* CONFIRMATION MODAL */}
      <ConfirmationModal
        isOpen={modalState.isOpen}
        onClose={() => setModalState({ isOpen: false, req: null, action: null, loading: false })}
        onConfirm={handleConfirmAction}
        title={modalState.action === 'accept' ? 'Accept Student Link Request?' : 'Reject Student Request?'}
        message={
          modalState.action === 'accept'
            ? `Accepting will officially link ${modalState.req?.student?.full_name || 'this student'} to your institution. You will gain access to verify their uploaded documents.`
            : `Rejecting will decline the connection request from ${modalState.req?.student?.full_name || 'this student'}.`
        }
        confirmLabel={modalState.action === 'accept' ? 'Accept Request' : 'Reject Request'}
        cancelLabel="Cancel"
        isDanger={modalState.action === 'reject'}
        isLoading={modalState.loading}
      />
    </div>
  );
};

export default StudentRequests;
