import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Download, Trash2, ExternalLink, ShieldCheck, UploadCloud } from 'lucide-react';
import { documentService } from '../../services/documentService';
import { useToast } from '../../context/ToastContext';
import PageHeader from '../../components/common/PageHeader';
import DataTable from '../../components/common/DataTable';
import StatusBadge from '../../components/common/StatusBadge';
import SearchInput from '../../components/common/SearchInput';
import ConfirmationModal from '../../components/common/ConfirmationModal';
import LoadingState from '../../components/common/LoadingState';

export const MyDocuments = () => {
  const { toast } = useToast();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [deleteModal, setDeleteModal] = useState({ isOpen: false, doc: null, loading: false });

  const fetchDocs = async () => {
    try {
      setLoading(true);
      const res = await documentService.getMyDocuments();
      setDocuments(res.data.documents || []);
    } catch (err) {
      toast.error('Unable to fetch documents.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleDelete = async () => {
    const d = deleteModal.doc;
    if (!d) return;

    try {
      setDeleteModal((prev) => ({ ...prev, loading: true }));
      const res = await documentService.deleteDocument(d.id);
      if (res.data?.partial_file_cleanup) {
        toast.warning(res.data.message || 'Document deleted from database, but some physical files could not be removed.');
      } else {
        toast.success(res.data?.message || 'Document and associated verification records deleted successfully');
      }
      setDeleteModal({ isOpen: false, doc: null, loading: false });
      fetchDocs();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to delete document.');
      setDeleteModal((prev) => ({ ...prev, loading: false }));
    }
  };

  const filtered = documents.filter((d) => {
    const q = search.toLowerCase();
    return (
      d.original_filename?.toLowerCase().includes(q) ||
      d.document_type?.toLowerCase().includes(q) ||
      d.file_hash?.toLowerCase().includes(q)
    );
  });

  const columns = [
    {
      header: 'Document Name',
      key: 'original_filename',
      render: (row) => (
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <FileText className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <p className="font-semibold text-slate-900 truncate max-w-[220px]">{row.original_filename}</p>
            <p className="text-[11px] text-slate-400 font-mono truncate max-w-[220px]">{row.file_hash?.slice(0, 16)}...</p>
          </div>
        </div>
      )
    },
    {
      header: 'Type',
      key: 'document_type',
      render: (row) => (
        <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-100 text-slate-700">
          {row.document_type}
        </span>
      )
    },
    {
      header: 'File Size',
      key: 'file_size',
      render: (row) => `${(row.file_size / 1024).toFixed(1)} KB`
    },
    {
      header: 'Uploaded Date',
      key: 'uploaded_at',
      render: (row) => row.uploaded_at ? new Date(row.uploaded_at).toLocaleDateString() : 'Recent'
    },
    {
      header: 'Actions',
      key: 'actions',
      className: 'text-right',
      render: (row) => (
        <div className="flex items-center justify-end gap-2">
          <a
            href={documentService.viewDocumentUrl(row.id)}
            target="_blank"
            rel="noreferrer"
            className="p-1.5 rounded-lg border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            title="View Raw Document"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
          <button
            onClick={() => setDeleteModal({ isOpen: true, doc: row, loading: false })}
            className="p-1.5 rounded-lg border border-rose-200 text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
            title="Delete Document"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      )
    }
  ];

  if (loading) {
    return <LoadingState message="Loading your document repository..." />;
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="My Documents"
        subtitle="Manage and view your uploaded academic credentials and certificates"
        action={
          <Link
            to="/student/verify"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-xs"
          >
            <UploadCloud className="w-4 h-4" />
            <span>Upload New Document</span>
          </Link>
        }
      />

      <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <SearchInput
            value={search}
            onChange={setSearch}
            placeholder="Search documents by name or type..."
            className="max-w-md w-full"
          />
          <span className="text-xs text-slate-500">{filtered.length} total files</span>
        </div>

        <DataTable
          columns={columns}
          data={filtered}
          emptyTitle="No documents found"
          emptyMessage="You haven't uploaded any documents matching your search filter."
          emptyAction={
            <Link
              to="/student/verify"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-900 text-white text-xs font-semibold rounded-lg hover:bg-slate-800"
            >
              Upload Document
            </Link>
          }
        />
      </div>

      <ConfirmationModal
        isOpen={deleteModal.isOpen}
        onClose={() => setDeleteModal({ isOpen: false, doc: null, loading: false })}
        onConfirm={handleDelete}
        title="Permanently Delete Document?"
        message={`Are you sure you want to permanently delete "${deleteModal.doc?.original_filename}"? All associated verification history, generated reports, and records will also be permanently deleted. This action cannot be undone.`}
        confirmLabel="Delete Document"
        isDanger={true}
        isLoading={deleteModal.loading}
      />
    </div>
  );
};

export default MyDocuments;
