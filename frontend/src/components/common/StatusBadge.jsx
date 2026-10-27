import React from 'react';
import { CheckCircle, XCircle, Clock, AlertTriangle, FileText, Ban } from 'lucide-react';

export const StatusBadge = ({ status, size = 'md' }) => {
  if (!status) return null;
  const s = String(status).toUpperCase();

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[11px] font-medium',
    md: 'px-2.5 py-1 text-xs font-semibold',
    lg: 'px-3 py-1.5 text-sm font-semibold'
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4'
  };

  const currentSize = sizeClasses[size] || sizeClasses.md;
  const iconSize = iconSizes[size] || iconSizes.md;

  let config = {
    bg: 'bg-slate-100 text-slate-700 border-slate-200',
    icon: <FileText className={iconSize} />,
    label: s
  };

  if (s === 'AUTHENTICATED' || s === 'VERIFIED' || s === 'ACCEPTED' || s === 'PASSED' || s === 'SUCCESS' || s === 'APPROVED') {
    config = {
      bg: 'bg-emerald-50 text-emerald-700 border-emerald-200/80',
      icon: <CheckCircle className={iconSize} />,
      label: s === 'ACCEPTED' ? 'Accepted' : s === 'PASSED' ? 'Passed' : s === 'SUCCESS' ? 'Success' : 'Authenticated'
    };
  } else if (s === 'SUPPORTED_DOCUMENT') {
    config = {
      bg: 'bg-emerald-50 text-emerald-700 border-emerald-200/80',
      icon: <CheckCircle className={iconSize} />,
      label: 'Supported Document'
    };
  } else if (s === 'UNKNOWN_DOCUMENT') {
    config = {
      bg: 'bg-amber-50 text-amber-700 border-amber-300',
      icon: <AlertTriangle className={iconSize} />,
      label: 'Unknown Document'
    };
  } else if (s === 'NOT_VERIFIED') {
    config = {
      bg: 'bg-amber-50 text-amber-700 border-amber-300',
      icon: <AlertTriangle className={iconSize} />,
      label: 'Not Verified'
    };
  } else if (s === 'VERIFICATION_FAILED' || s === 'NOT_AUTHENTICATED' || s === 'NOT AUTHENTICATED' || s === 'REJECTED' || s === 'FAILED' || s === 'REMOVED') {
    config = {
      bg: 'bg-rose-50 text-rose-700 border-rose-200/80',
      icon: <XCircle className={iconSize} />,
      label: s === 'VERIFICATION_FAILED' ? 'Verification Failed' : s === 'REJECTED' ? 'Rejected' : s === 'FAILED' ? 'Failed' : s === 'REMOVED' ? 'Removed' : 'Not Authenticated'
    };
  } else if (s === 'PENDING' || s === 'PROCESSING' || s === 'ANALYZING') {
    config = {
      bg: 'bg-amber-50 text-amber-700 border-amber-200/80',
      icon: <Clock className={iconSize} />,
      label: s === 'PENDING' ? 'Pending' : 'Processing'
    };
  } else if (s === 'SUSPICIOUS' || s === 'FLAGGED' || s === 'WARNING') {
    config = {
      bg: 'bg-amber-100 text-amber-900 border-amber-300',
      icon: <AlertTriangle className={iconSize} />,
      label: 'Suspicious'
    };
  } else if (s === 'UNLINKED') {
    config = {
      bg: 'bg-slate-100 text-slate-600 border-slate-300',
      icon: <Ban className={iconSize} />,
      label: 'Unlinked'
    };
  } else if (s === 'UNAVAILABLE') {
    config = {
      bg: 'bg-amber-50 text-amber-700 border-amber-200',
      icon: <Clock className={iconSize} />,
      label: 'Unavailable'
    };
  } else if (s === 'IN_PROGRESS' || s === 'IN PROGRESS') {
    config = {
      bg: 'bg-blue-50 text-blue-700 border-blue-200',
      icon: <Clock className={iconSize} />,
      label: 'In Progress'
    };
  } else if (s === 'ERROR') {
    config = {
      bg: 'bg-rose-50 text-rose-700 border-rose-200',
      icon: <XCircle className={iconSize} />,
      label: 'Error'
    };
  } else if (s === 'NOT_APPLICABLE' || s === 'N/A' || s === 'NOT APPLICABLE' || s === 'SKIPPED') {
    config = {
      bg: 'bg-slate-100 text-slate-500 border-slate-200',
      icon: null,
      label: 'Not Applicable'
    };
  }

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md border ${config.bg} ${currentSize}`}>
      {config.icon}
      <span>{config.label}</span>
    </span>
  );
};

export default StatusBadge;
