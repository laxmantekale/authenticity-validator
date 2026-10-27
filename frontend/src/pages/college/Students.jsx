import React, { useState, useEffect } from 'react';
import { Users, Search, UserMinus, FileText, Mail, Phone, ExternalLink, Loader2, CheckCircle2 } from 'lucide-react';
import { collegeService } from '../../services/collegeService';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import DataTable from '../../components/common/DataTable';
import StatusBadge from '../../components/common/StatusBadge';
import SearchInput from '../../components/common/SearchInput';
import ConfirmationModal from '../../components/common/ConfirmationModal';
import LoadingState from '../../components/common/LoadingState';

export const Students = () => {
  const { toast } = useToast();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  // Remove Modal State
  const [removeModal, setRemoveModal] = useState({ isOpen: false, student: null, loading: false });

  // View Documents Modal State
  const [docModal, setDocModal] = useState({ isOpen: false, student: null, docs: [], loading: false });

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const res = await collegeService.getStudents();
      setStudents(res.data.students || []);
    } catch (err) {
      toast.error('Unable to fetch enrolled students.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, []);

  const handleConfirmRemove = async () => {
    const s = removeModal.student;
    if (!s) return;

    try {
      setRemoveModal((prev) => ({ ...prev, loading: true }));
      await collegeService.removeStudent(s.id);
      toast.success('Student removed successfully. Historical records preserved.');
      setRemoveModal({ isOpen: false, student: null, loading: false });
      fetchStudents();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to remove student.');
      setRemoveModal((prev) => ({ ...prev, loading: false }));
    }
  };

  const handleViewDocuments = async (student) => {
    try {
      setDocModal({ isOpen: true, student, docs: [], loading: true });
      const res = await collegeService.getStudentDocuments(student.id);
      setDocModal({ isOpen: true, student, docs: res.data.documents || [], loading: false });
    } catch (err) {
      toast.error('Failed to load student documents.');
      setDocModal({ isOpen: false, student: null, docs: [], loading: false });
    }
  };

  const filtered = students.filter((s) => {
    const q = search.toLowerCase();
    return (
      s.full_name?.toLowerCase().includes(q) ||
      s.student_id?.toLowerCase().includes(q) ||
      s.email?.toLowerCase().includes(q)
    );
  });

  const columns = [
    {
      header: 'Student Name',
      key: 'full_name',
      render: (row) => (
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-blue-50 text-blue-700 flex items-center justify-center font-bold text-xs shrink-0">
            {row.full_name ? row.full_name.charAt(0) : 'S'}
          </div>
          <div>
            <p className="font-semibold text-slate-900">{row.full_name}</p>
            <p className="text-[11px] text-slate-400">{row.email}</p>
          </div>
        </div>
      )
    },
    {
      header: 'Student ID',
      key: 'student_id',
      render: (row) => (
        <span className="font-mono text-xs font-semibold text-slate-800 bg-slate-100 px-2 py-0.5 rounded">
          {row.student_id}
        </span>
      )
    },
    {
      header: 'Mobile',
      key: 'mobile',
      render: (row) => row.mobile || 'N/A'
    },
    {
      header: 'Linked Date',
      key: 'linked_at',
      render: (row) => row.linked_at ? new Date(row.linked_at).toLocaleDateString() : 'Active'
    },
    {
      header: 'Status',
      key: 'status',
      render: () => <StatusBadge status="ACCEPTED" size="sm" />
    },
    {
      header: 'Actions',
      key: 'actions',
      className: 'text-right',
      render: (row) => (
        <div className="flex items-center justify-end gap-2">
          <button
            onClick={() => handleViewDocuments(row)}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold transition-colors cursor-pointer"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Documents ({row.total_documents || 0})</span>
          </button>
          <button
            onClick={() => setRemoveModal({ isOpen: true, student: row, loading: false })}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-rose-200 text-rose-600 hover:bg-rose-50 text-xs font-semibold transition-colors cursor-pointer"
          >
            <UserMinus className="w-3.5 h-3.5" />
            <span>Remove</span>
          </button>
        </div>
      )
    }
  ];

  if (loading) {
    return <LoadingState message="Loading enrolled student records..." />;
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Enrolled Students"
        subtitle="Manage active student linkages, review verified credentials, and manage enrollment"
        badge={`${students.length} Linked Students`}
      />

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
          <SearchInput
            value={search}
            onChange={setSearch}
            placeholder="Search students by name, ID, or email..."
            className="max-w-md w-full"
          />
          <span className="text-xs text-slate-500">{filtered.length} active students</span>
        </div>

        <DataTable
          columns={columns}
          data={filtered}
          emptyTitle="No enrolled students"
          emptyMessage="No active student links match your query. Review pending requests to link students."
        />
      </div>

      {/* REMOVE STUDENT CONFIRMATION MODAL */}
      <ConfirmationModal
        isOpen={removeModal.isOpen}
        onClose={() => setRemoveModal({ isOpen: false, student: null, loading: false })}
        onConfirm={handleConfirmRemove}
        title="Remove Student?"
        message={`This student (${removeModal.student?.full_name}) will no longer be linked with your institution. Their account and historical verification records will remain محفوظ.`}
        confirmLabel="Remove Student"
        cancelLabel="Cancel"
        isDanger={true}
        isLoading={removeModal.loading}
      />

      {/* STUDENT DOCUMENTS MODAL */}
      {docModal.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-2xl w-full p-6 space-y-4 max-h-[85vh] flex flex-col">
            
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Documents for {docModal.student?.full_name}
                </h3>
                <p className="text-xs text-slate-500">Student ID: {docModal.student?.student_id}</p>
              </div>
              <button
                onClick={() => setDocModal({ isOpen: false, student: null, docs: [], loading: false })}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-1 min-h-[200px]">
              {docModal.loading ? (
                <LoadingState message="Loading documents..." />
              ) : docModal.docs.length === 0 ? (
                <div className="p-6 text-center text-xs text-slate-500">
                  This student has not uploaded any credentials yet.
                </div>
              ) : (
                docModal.docs.map((d) => (
                  <div
                    key={d.id}
                    className="p-3.5 rounded-xl border border-slate-200 hover:bg-slate-50 flex items-center justify-between gap-3"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                        <FileText className="w-4 h-4" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs font-bold text-slate-900 truncate">{d.original_filename}</p>
                        <p className="text-[11px] text-slate-400">{d.document_type} • {(d.file_size / 1024).toFixed(1)} KB</p>
                      </div>
                    </div>

                    <a
                      href={`/api/documents/${d.id}/view`}
                      target="_blank"
                      rel="noreferrer"
                      className="px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold flex items-center gap-1.5 shrink-0"
                    >
                      <span>View File</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                ))
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setDocModal({ isOpen: false, student: null, docs: [], loading: false })}
                className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50"
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

export default Students;
