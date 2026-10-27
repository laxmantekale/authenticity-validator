import React, { useState, useEffect } from 'react';
import {
  Building2,
  Mail,
  MapPin,
  Search,
  Plus,
  Unlink,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2,
  ArrowRight,
  ShieldCheck,
  QrCode,
  RefreshCw
} from 'lucide-react';
import { studentService } from '../../services/studentService';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import SectionCard from '../../components/common/SectionCard';
import StatusBadge from '../../components/common/StatusBadge';
import EmptyState from '../../components/common/EmptyState';
import LoadingState from '../../components/common/LoadingState';
import ConfirmationModal from '../../components/common/ConfirmationModal';
import SearchInput from '../../components/common/SearchInput';

export const MyColleges = () => {
  const { toast } = useToast();
  const [data, setData] = useState({ linked_colleges: [], pending_requests: [], rejected_requests: [] });
  const [loading, setLoading] = useState(true);

  // Unlink Modal State
  const [unlinkModal, setUnlinkModal] = useState({ isOpen: false, college: null, loading: false });

  // Add College Modal State
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [requestingId, setRequestingId] = useState(null);

  const [refreshing, setRefreshing] = useState(false);

  const fetchColleges = async (isManual = false) => {
    try {
      if (isManual) setRefreshing(true);
      else setLoading(true);
      const res = await studentService.getColleges();
      setData(res.data);
      if (isManual) toast.success('Colleges list refreshed');
    } catch (err) {
      toast.error('Unable to retrieve connected colleges.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchColleges();
  }, []);

  // Search colleges when modal is open
  const handleSearch = async (q) => {
    setSearchQuery(q);
    try {
      setSearching(true);
      const res = await studentService.searchColleges(q);
      setSearchResults(res.data.colleges || []);
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setSearching(false);
    }
  };

  const handleOpenAddModal = () => {
    setAddModalOpen(true);
    handleSearch('');
  };

  const handleSendRequest = async (collegeId) => {
    try {
      setRequestingId(collegeId);
      await studentService.requestLink(collegeId);
      toast.success('Connection request sent to institution for review!');
      fetchColleges();
      setAddModalOpen(false);
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to send connection request.');
    } finally {
      setRequestingId(null);
    }
  };

  const handleConfirmUnlink = async () => {
    const col = unlinkModal.college;
    if (!col) return;

    try {
      setUnlinkModal((prev) => ({ ...prev, loading: true }));
      await studentService.unlinkCollege(col.college_id || col.id);
      toast.success('College unlinked successfully. All historical records preserved.');
      setUnlinkModal({ isOpen: false, college: null, loading: false });
      fetchColleges();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to unlink college.');
      setUnlinkModal((prev) => ({ ...prev, loading: false }));
    }
  };

  if (loading) {
    return <LoadingState message="Loading your college connections..." />;
  }

  const linked = data.linked_colleges || [];
  const pending = data.pending_requests || [];
  const rejected = data.rejected_requests || [];

  return (
    <div className="space-y-8">
      
      <PageHeader
        title="My Colleges"
        subtitle="Manage your connected academic institutions and access shared verification services."
        action={
          <div className="flex items-center gap-2">
            <button
              onClick={() => fetchColleges(true)}
              disabled={refreshing}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-60"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            <button
              onClick={handleOpenAddModal}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Connect to College</span>
            </button>
          </div>
        }
      />

      {/* 1. LINKED COLLEGES SECTION */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900">Linked Colleges ({linked.length})</h2>
        </div>

        {linked.length === 0 ? (
          <EmptyState
            icon={Building2}
            title="No connected colleges"
            message="You are not currently linked with any college. Connecting allows institutions to verify your documents directly."
            actionLabel="Search & Connect College"
            onAction={handleOpenAddModal}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {linked.map((link) => {
              const col = link.college || {};
              return (
                <div
                  key={link.id}
                  className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-200 text-blue-700 flex items-center justify-center font-bold text-base shrink-0">
                        {col.college_name ? col.college_name.charAt(0) : 'C'}
                      </div>
                      <StatusBadge status="ACCEPTED" />
                    </div>

                    <div>
                      <h3 className="text-sm font-bold text-slate-900 leading-snug">{col.college_name || 'Academic Institution'}</h3>
                      <p className="text-[11px] text-slate-500 font-mono mt-0.5">Code: {col.college_id}</p>
                    </div>

                    <div className="space-y-1.5 pt-2 border-t border-slate-100 text-xs text-slate-600">
                      <div className="flex items-center gap-2">
                        <Mail className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        <span className="truncate">{col.official_email}</span>
                      </div>
                      {link.accepted_at && (
                        <p className="text-[11px] text-slate-400">
                          Connected: {new Date(link.accepted_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-[11px] text-emerald-600 font-semibold flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Verified Link</span>
                    </span>
                    <button
                      onClick={() => setUnlinkModal({ isOpen: true, college: col, loading: false })}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-rose-600 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer border border-transparent hover:border-rose-200"
                    >
                      <Unlink className="w-3.5 h-3.5" />
                      <span>Unlink College</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 2. PENDING REQUESTS SECTION */}
      {pending.length > 0 && (
        <SectionCard
          title={`Pending Connection Requests (${pending.length})`}
          subtitle="Awaiting administrative review and approval from the institution"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {pending.map((link) => {
              const col = link.college || {};
              return (
                <div key={link.id} className="p-4 rounded-xl border border-amber-200 bg-amber-50/40 flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className="w-9 h-9 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-sm shrink-0">
                      {col.college_name ? col.college_name.charAt(0) : 'C'}
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900">{col.college_name}</h4>
                      <p className="text-[11px] text-slate-500 font-mono">Code: {col.college_id}</p>
                      <p className="text-[10px] text-slate-400 mt-1">
                        Requested: {link.requested_at ? new Date(link.requested_at).toLocaleDateString() : 'Pending'}
                      </p>
                    </div>
                  </div>
                  <StatusBadge status="PENDING" size="sm" />
                </div>
              );
            })}
          </div>
        </SectionCard>
      )}

      {/* 3. REJECTED REQUESTS SECTION (IF ANY) */}
      {rejected.length > 0 && (
        <SectionCard
          title={`Declined Requests (${rejected.length})`}
          subtitle="Requests declined by the institution (you may re-apply if appropriate)"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {rejected.map((link) => {
              const col = link.college || {};
              return (
                <div key={link.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 flex items-start justify-between gap-3">
                  <div>
                    <h4 className="text-xs font-bold text-slate-900">{col.college_name}</h4>
                    <p className="text-[11px] text-slate-500 font-mono">Code: {col.college_id}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status="REJECTED" size="sm" />
                    <button
                      onClick={() => handleSendRequest(col.id)}
                      className="px-2.5 py-1 bg-slate-900 text-white rounded text-[11px] font-semibold hover:bg-slate-800"
                    >
                      Re-apply
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </SectionCard>
      )}

      {/* UNLINK CONFIRMATION MODAL */}
      <ConfirmationModal
        isOpen={unlinkModal.isOpen}
        onClose={() => setUnlinkModal({ isOpen: false, college: null, loading: false })}
        onConfirm={handleConfirmUnlink}
        title="Disconnect from Institution?"
        message={`Are you sure you want to disconnect from ${unlinkModal.college?.college_name || 'this college'}? All your uploaded documents, verification history, and official reports will remain fully preserved.`}
        confirmLabel="Disconnect College"
        cancelLabel="Cancel"
        isDanger={true}
        isLoading={unlinkModal.loading}
      />

      {/* SEARCH / ADD COLLEGE MODAL */}
      {addModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-lg w-full p-6 space-y-4 max-h-[85vh] flex flex-col">
            
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="text-base font-bold text-slate-900">Connect to an Academic Institution</h3>
                <p className="text-xs text-slate-500">Search by institution name or official college code</p>
              </div>
              <button
                onClick={() => setAddModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            <SearchInput
              value={searchQuery}
              onChange={handleSearch}
              placeholder="Search e.g. National Institute of Technology or NIT..."
            />

            <div className="flex-1 overflow-y-auto space-y-3 pr-1 min-h-[220px]">
              {searching ? (
                <LoadingState message="Searching institutions..." />
              ) : searchResults.length === 0 ? (
                <EmptyState
                  title="No institutions found"
                  message="Try searching with a different college name or code."
                />
              ) : (
                searchResults.map((col) => {
                  const isLinked = linked.some((l) => l.college_id === col.id);
                  const isPending = pending.some((l) => l.college_id === col.id);

                  return (
                    <div
                      key={col.id}
                      className="p-3.5 rounded-xl border border-slate-200 hover:border-slate-300 hover:bg-slate-50 flex items-center justify-between gap-3 transition-colors"
                    >
                      <div className="min-w-0">
                        <h4 className="text-xs font-bold text-slate-900 truncate">{col.college_name}</h4>
                        <p className="text-[11px] text-slate-500 font-mono">Code: {col.college_id}</p>
                        <p className="text-[11px] text-slate-400 truncate">{col.address || col.official_email}</p>
                      </div>

                      <div className="shrink-0">
                        {isLinked ? (
                          <StatusBadge status="ACCEPTED" size="sm" />
                        ) : isPending ? (
                          <StatusBadge status="PENDING" size="sm" />
                        ) : (
                          <button
                            onClick={() => handleSendRequest(col.id)}
                            disabled={requestingId === col.id}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs cursor-pointer disabled:bg-blue-400"
                          >
                            {requestingId === col.id ? (
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                            ) : (
                              <>
                                <span>Connect</span>
                                <ArrowRight className="w-3 h-3" />
                              </>
                            )}
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
                onClick={() => setAddModalOpen(false)}
                className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 cursor-pointer"
              >
                Close
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

export default MyColleges;
