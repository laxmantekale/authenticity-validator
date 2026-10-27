import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FolderOpen,
  FileText,
  Search,
  ShieldCheck,
  User,
  UploadCloud,
  Trash2,
  Eye,
  RefreshCw,
  Filter,
  ArrowUpDown,
  Plus,
  Users,
  CheckCircle2,
  Calendar,
  Mail,
  ExternalLink,
  Loader2
} from 'lucide-react';
import { documentService } from '../../services/documentService';
import { collegeService } from '../../services/collegeService';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import DataTable from '../../components/common/DataTable';
import StatusBadge from '../../components/common/StatusBadge';
import SearchInput from '../../components/common/SearchInput';
import LoadingState from '../../components/common/LoadingState';
import Pagination from '../../components/common/Pagination';
import ConfirmationModal from '../../components/common/ConfirmationModal';
import Modal from '../../components/common/Modal';
import DocumentDetailsModal from '../../components/documents/DocumentDetailsModal';

export const Documents = () => {
  const { toast } = useToast();
  const navigate = useNavigate();

  // Active Tab: 'direct' or 'linked'
  const [activeTab, setActiveTab] = useState('direct');

  // Direct Documents & Linked Students state
  const [directDocs, setDirectDocs] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Filters & search
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [sortBy, setSortBy] = useState('date_desc');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Modals state
  const [previewDoc, setPreviewDoc] = useState(null);
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, doc: null, loading: false });
  const [uploadModalOpen, setUploadModalOpen] = useState(false);

  // Student Documents Modal
  const [studentDocsModal, setStudentDocsModal] = useState({
    isOpen: false,
    student: null,
    docs: [],
    loading: false
  });

  // Upload Form state
  const [uploadForm, setUploadForm] = useState({
    file: null,
    document_type: 'Degree Certificate',
    document_title: ''
  });
  const [uploading, setUploading] = useState(false);

  const fetchData = async (isManual = false) => {
    try {
      if (isManual) setRefreshing(true);
      else setLoading(true);

      const [directRes, studentsRes] = await Promise.all([
        documentService.getDirectDocuments().catch(() => ({ data: { documents: [] } })),
        collegeService.getStudents().catch(() => ({ data: { students: [] } }))
      ]);

      setDirectDocs(directRes.data.documents || []);
      setStudents(studentsRes.data.students || []);

      if (isManual) toast.success('Documents and student records synchronized');
    } catch (err) {
      toast.error('Unable to fetch institutional records.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Handle Delete Direct Document
  const handleConfirmDelete = async () => {
    const doc = deleteModal.doc;
    if (!doc) return;

    try {
      setDeleteModal((prev) => ({ ...prev, loading: true }));
      const res = await documentService.deleteDocument(doc.id);
      if (res.data?.partial_file_cleanup) {
        toast.warning(res.data.message || 'Document deleted from database, but some physical files could not be removed.');
      } else {
        toast.success(res.data?.message || 'Document and all associated verification records deleted successfully');
      }
      setDeleteModal({ isOpen: false, doc: null, loading: false });
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to remove document.');
      setDeleteModal((prev) => ({ ...prev, loading: false }));
    }
  };

  // Handle Direct Document Upload
  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadForm.file) {
      toast.error('Please select a PDF or image file to upload.');
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', uploadForm.file);
      formData.append('document_type', uploadForm.document_type);
      formData.append('document_title', uploadForm.document_title || uploadForm.file.name);

      await documentService.uploadDocument(formData);
      toast.success('Document uploaded successfully to institutional repository.');
      setUploadModalOpen(false);
      setUploadForm({ file: null, document_type: 'Degree Certificate', document_title: '' });
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to upload document.');
    } finally {
      setUploading(false);
    }
  };

  // View Student Documents Modal
  const handleOpenStudentDocs = async (student) => {
    setStudentDocsModal({ isOpen: true, student, docs: [], loading: true });
    try {
      const res = await collegeService.getStudentDocuments(student.id);
      setStudentDocsModal({
        isOpen: true,
        student,
        docs: res.data.documents || [],
        loading: false
      });
    } catch (err) {
      toast.error('Failed to load student documents.');
      setStudentDocsModal({ isOpen: false, student: null, docs: [], loading: false });
    }
  };

  // Filter & Sort for Tab 1 (Direct Docs)
  const filteredDirectDocs = useMemo(() => {
    let result = directDocs.filter((d) => {
      const q = search.toLowerCase();
      const matchesSearch =
        (d.original_filename || '').toLowerCase().includes(q) ||
        (d.document_type || '').toLowerCase().includes(q) ||
        (d.verification_code || '').toLowerCase().includes(q);

      if (statusFilter === 'ALL') return matchesSearch;
      return matchesSearch && (d.verification_status || 'PENDING').toUpperCase() === statusFilter;
    });

    result.sort((a, b) => {
      if (sortBy === 'date_desc') return new Date(b.uploaded_at || 0) - new Date(a.uploaded_at || 0);
      if (sortBy === 'date_asc') return new Date(a.uploaded_at || 0) - new Date(b.uploaded_at || 0);
      if (sortBy === 'name_asc') return (a.original_filename || '').localeCompare(b.original_filename || '');
      if (sortBy === 'name_desc') return (b.original_filename || '').localeCompare(a.original_filename || '');
      return 0;
    });

    return result;
  }, [directDocs, search, statusFilter, sortBy]);

  // Filter & Sort for Tab 2 (Linked Students)
  const filteredStudents = useMemo(() => {
    let result = students.filter((s) => {
      const q = search.toLowerCase();
      return (
        (s.full_name || '').toLowerCase().includes(q) ||
        (s.student_id || '').toLowerCase().includes(q) ||
        (s.email || '').toLowerCase().includes(q)
      );
    });

    result.sort((a, b) => {
      if (sortBy === 'name_asc') return (a.full_name || '').localeCompare(b.full_name || '');
      if (sortBy === 'name_desc') return (b.full_name || '').localeCompare(a.full_name || '');
      if (sortBy === 'date_desc') return new Date(b.linked_at || b.created_at || 0) - new Date(a.linked_at || a.created_at || 0);
      if (sortBy === 'date_asc') return new Date(a.linked_at || a.created_at || 0) - new Date(b.linked_at || b.created_at || 0);
      return 0;
    });

    return result;
  }, [students, search, sortBy]);

  const currentDataset = activeTab === 'direct' ? filteredDirectDocs : filteredStudents;
  const totalPages = Math.ceil(currentDataset.length / pageSize) || 1;
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return currentDataset.slice(start, start + pageSize);
  }, [currentDataset, currentPage, pageSize]);

  useEffect(() => {
    setCurrentPage(1);
  }, [activeTab, search, statusFilter, sortBy]);

  // Columns for Direct Upload Table
  const directColumns = [
    {
      header: 'Document Name',
      key: 'original_filename',
      render: (row) => (
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <FileText className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <p className="font-semibold text-slate-900 truncate">{row.original_filename}</p>
            <p className="text-[11px] text-slate-400 font-mono truncate">Code: {row.verification_code || `DOC-${row.id}`}</p>
          </div>
        </div>
      )
    },
    {
      header: 'Document Type',
      key: 'document_type',
      render: (row) => (
        <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700">
          {row.document_type || 'Academic Record'}
        </span>
      )
    },
    {
      header: 'Upload Date',
      key: 'uploaded_at',
      render: (row) => row.uploaded_at ? new Date(row.uploaded_at).toLocaleDateString() : 'Recent'
    },
    {
      header: 'Status',
      key: 'verification_status',
      render: (row) => <StatusBadge status={row.verification_status || 'PENDING'} />
    },
    {
      header: 'Actions',
      key: 'actions',
      className: 'text-right',
      render: (row) => (
        <div className="flex items-center justify-end gap-1.5">
          <button
            type="button"
            onClick={() => setPreviewDoc(row)}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition-colors cursor-pointer"
            title="View Details & Preview"
          >
            <Eye className="w-3.5 h-3.5 text-slate-600" />
            <span className="hidden sm:inline">View</span>
          </button>

          <button
            type="button"
            onClick={() => navigate('/college/verification')}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold transition-colors cursor-pointer"
            title="Verify Document"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Verify</span>
          </button>

          <button
            type="button"
            onClick={() => setDeleteModal({ isOpen: true, doc: row, loading: false })}
            className="inline-flex items-center gap-1 p-1.5 rounded-lg hover:bg-rose-50 text-rose-600 transition-colors cursor-pointer"
            title="Delete Document"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      )
    }
  ];

  // Columns for Linked Student Table
  const linkedStudentColumns = [
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
            <p className="text-[11px] text-slate-400">{row.mobile || 'Student'}</p>
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
      header: 'Email Address',
      key: 'email',
      render: (row) => (
        <div className="flex items-center gap-1.5 text-xs text-slate-600">
          <Mail className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span>{row.email || 'N/A'}</span>
        </div>
      )
    },
    {
      header: 'Status',
      key: 'status',
      render: () => (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          <CheckCircle2 className="w-3 h-3" />
          <span>Active Connection</span>
        </span>
      )
    },
    {
      header: 'Connected Date',
      key: 'linked_at',
      render: (row) => (
        <span className="text-xs text-slate-600">
          {row.linked_at ? new Date(row.linked_at).toLocaleDateString() : row.created_at ? new Date(row.created_at).toLocaleDateString() : 'Active'}
        </span>
      )
    },
    {
      header: 'Actions',
      key: 'actions',
      className: 'text-right',
      render: (row) => (
        <div className="flex items-center justify-end">
          <button
            type="button"
            onClick={() => handleOpenStudentDocs(row)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold rounded-lg transition-colors cursor-pointer"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>View Documents</span>
          </button>
        </div>
      )
    }
  ];

  if (loading) {
    return <LoadingState message="Loading institutional document repository..." />;
  }

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <PageHeader
        title="Institutional Documents"
        subtitle="Manage directly uploaded candidate records and review credentials submitted by connected students"
        badge={`${directDocs.length} Direct • ${students.length} Connected Students`}
        action={
          <div className="flex items-center gap-2">
            <button
              onClick={() => fetchData(true)}
              disabled={refreshing}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer disabled:opacity-60"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            <button
              onClick={() => setUploadModalOpen(true)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Upload Document</span>
            </button>
          </div>
        }
      />

      {/* TABS SELECTOR */}
      <div className="flex border-b border-slate-200 bg-white rounded-t-xl px-2 pt-2 gap-2">
        <button
          onClick={() => setActiveTab('direct')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
            activeTab === 'direct'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FolderOpen className="w-4 h-4" />
          <span>Direct Upload</span>
          <span className={`px-2 py-0.5 rounded-full text-[10px] ${activeTab === 'direct' ? 'bg-blue-100 text-blue-700 font-bold' : 'bg-slate-100 text-slate-600'}`}>
            {directDocs.length}
          </span>
        </button>

        <button
          onClick={() => setActiveTab('linked')}
          className={`flex items-center gap-2 px-4 py-2.5 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
            activeTab === 'linked'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Users className="w-4 h-4" />
          <span>Linked Students</span>
          <span className={`px-2 py-0.5 rounded-full text-[10px] ${activeTab === 'linked' ? 'bg-blue-100 text-blue-700 font-bold' : 'bg-slate-100 text-slate-600'}`}>
            {students.length}
          </span>
        </button>
      </div>

      {/* TAB CONTENT & DATA TABLE */}
      <div className="bg-white rounded-b-xl border border-slate-200 shadow-xs overflow-hidden -mt-6">
        
        {/* Filter Bar */}
        <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50/50">
          <SearchInput
            value={search}
            onChange={setSearch}
            placeholder={
              activeTab === 'direct'
                ? 'Search direct documents by name, type, or code...'
                : 'Search connected students by name, ID, or email...'
            }
            className="max-w-md w-full"
          />

          <div className="flex flex-wrap items-center gap-3">
            {activeTab === 'direct' && (
              <div className="flex items-center gap-1.5 text-xs text-slate-500">
                <Filter className="w-3.5 h-3.5" />
                <span>Status:</span>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-900/10"
                >
                  <option value="ALL">All Statuses</option>
                  <option value="PENDING">Pending</option>
                  <option value="AUTHENTICATED">Authenticated</option>
                  <option value="NOT_AUTHENTICATED">Not Authenticated</option>
                  <option value="SUSPICIOUS">Suspicious</option>
                </select>
              </div>
            )}

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

        {/* Data Table */}
        <DataTable
          columns={activeTab === 'direct' ? directColumns : linkedStudentColumns}
          data={paginatedData}
          emptyTitle={activeTab === 'direct' ? 'No direct documents uploaded' : 'No connected students found'}
          emptyMessage={
            activeTab === 'direct'
              ? 'Upload academic certificates directly to evaluate authenticity.'
              : 'Students who link with your institution will appear here.'
          }
          actionLabel={activeTab === 'direct' ? 'Upload First Document' : undefined}
          onAction={activeTab === 'direct' ? () => setUploadModalOpen(true) : undefined}
        />

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs text-slate-500">
              Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, currentDataset.length)} of {currentDataset.length} entries
            </span>
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
            />
          </div>
        )}
      </div>

      {/* MODAL 1: Upload Direct Document */}
      <Modal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        title="Direct Document Upload"
        maxWidth="max-w-lg"
      >
        <form onSubmit={handleUploadSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Document File (PDF / Images)</label>
            <input
              type="file"
              required
              accept=".pdf,.png,.jpg,.jpeg,.webp"
              onChange={(e) => setUploadForm({ ...uploadForm, file: e.target.files[0] })}
              className="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-slate-300 rounded-lg p-1.5"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Document Title / Candidate Identifier</label>
            <input
              type="text"
              value={uploadForm.document_title}
              onChange={(e) => setUploadForm({ ...uploadForm, document_title: e.target.value })}
              placeholder="e.g., Degree Certificate - Candidate 2024"
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/10 shadow-xs"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Document Classification</label>
            <select
              value={uploadForm.document_type}
              onChange={(e) => setUploadForm({ ...uploadForm, document_type: e.target.value })}
              className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900/10 shadow-xs"
            >
              <option value="Degree Certificate">Degree Certificate</option>
              <option value="Marks Memo / Marksheet">Marks Memo / Marksheet</option>
              <option value="Provisional Certificate">Provisional Certificate</option>
              <option value="Transfer Certificate">Transfer Certificate</option>
              <option value="Academic Transcript">Academic Transcript</option>
            </select>
          </div>

          <div className="pt-3 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setUploadModalOpen(false)}
              className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={uploading}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-xs disabled:opacity-50"
            >
              <UploadCloud className="w-4 h-4" />
              <span>{uploading ? 'Uploading...' : 'Upload Document'}</span>
            </button>
          </div>
        </form>
      </Modal>

      {/* MODAL 2: Linked Student Documents (View & Verify only; NO Delete) */}
      <Modal
        isOpen={studentDocsModal.isOpen}
        onClose={() => setStudentDocsModal({ isOpen: false, student: null, docs: [], loading: false })}
        title={`Documents for ${studentDocsModal.student?.full_name || 'Student'} (${studentDocsModal.student?.student_id || ''})`}
        maxWidth="max-w-3xl"
      >
        <div className="space-y-4">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between text-xs">
            <div>
              <p className="font-semibold text-slate-900">{studentDocsModal.student?.full_name}</p>
              <p className="text-slate-500 text-[11px]">{studentDocsModal.student?.email || 'Student Email'}</p>
            </div>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              {studentDocsModal.docs.length} Uploaded Documents
            </span>
          </div>

          {studentDocsModal.loading ? (
            <div className="py-12 flex flex-col items-center justify-center text-slate-500 text-xs">
              <Loader2 className="w-6 h-6 animate-spin text-blue-600 mb-2" />
              <span>Loading student documents...</span>
            </div>
          ) : studentDocsModal.docs.length === 0 ? (
            <div className="py-10 text-center text-xs text-slate-500 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
              <FileText className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="font-medium text-slate-700">No documents found</p>
              <p className="text-slate-400 mt-0.5">This student has not uploaded any documents yet.</p>
            </div>
          ) : (
            <div className="overflow-x-auto border border-slate-200 rounded-xl">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50 text-slate-500 font-semibold text-[11px]">
                    <th className="px-4 py-2.5">Document Title</th>
                    <th className="px-4 py-2.5">Type</th>
                    <th className="px-4 py-2.5">Upload Date</th>
                    <th className="px-4 py-2.5">Status</th>
                    <th className="px-4 py-2.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 bg-white">
                  {studentDocsModal.docs.map((doc) => (
                    <tr key={doc.id} className="hover:bg-slate-50/60">
                      <td className="px-4 py-3 font-semibold text-slate-900">
                        {doc.original_filename}
                      </td>
                      <td className="px-4 py-3 text-slate-600">
                        <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700">
                          {doc.document_type || 'Academic Record'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-500 text-[11px]">
                        {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : 'Recent'}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={doc.verification_status || 'PENDING'} />
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            type="button"
                            onClick={() => setPreviewDoc(doc)}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition-colors"
                          >
                            <Eye className="w-3.5 h-3.5" />
                            <span>View</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setStudentDocsModal({ isOpen: false, student: null, docs: [], loading: false });
                              navigate('/college/verification');
                            }}
                            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold transition-colors"
                          >
                            <ShieldCheck className="w-3.5 h-3.5" />
                            <span>Verify</span>
                          </button>
                          {/* Note: NO Delete button permitted for student documents */}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="pt-2 flex justify-end">
            <button
              type="button"
              onClick={() => setStudentDocsModal({ isOpen: false, student: null, docs: [], loading: false })}
              className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50"
            >
              Close
            </button>
          </div>
        </div>
      </Modal>

      {/* MODAL 3: Document Details / Preview */}
      {previewDoc && (
        <DocumentDetailsModal
          isOpen={!!previewDoc}
          onClose={() => setPreviewDoc(null)}
          document={previewDoc}
        />
      )}

      {/* MODAL 4: Soft-Delete Confirmation */}
      <ConfirmationModal
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal({ isOpen: false, doc: null, loading: false })}
        onConfirm={handleConfirmDelete}
        loading={deleteModal.loading}
        title="Permanently Delete Document"
        message="Are you sure you want to permanently delete this document? All associated verification history, generated reports, and records will also be permanently deleted. This action cannot be undone."
        confirmText="Delete Document"
        confirmVariant="danger"
      />

    </div>
  );
};

export default Documents;
