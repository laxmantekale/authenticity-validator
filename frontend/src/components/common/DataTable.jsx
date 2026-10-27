import React from 'react';
import EmptyState from './EmptyState';
import { TableSkeleton } from './LoadingState';

export const DataTable = ({
  columns = [],
  data = [],
  keyField = 'id',
  isLoading = false,
  emptyTitle = 'No data available',
  emptyMessage = 'No records match your query.',
  emptyAction,
  className = ''
}) => {
  if (isLoading) {
    return <TableSkeleton rows={4} cols={columns.length || 4} />;
  }

  if (!data || data.length === 0) {
    return <EmptyState title={emptyTitle} message={emptyMessage} action={emptyAction} />;
  }

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full text-left border-collapse text-xs">
        <thead>
          <tr className="border-b border-slate-200 bg-slate-50/75 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
            {columns.map((col, idx) => (
              <th key={col.key || idx} className={`px-4 py-3 ${col.className || ''}`}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white text-slate-700">
          {data.map((row, rowIdx) => (
            <tr key={row[keyField] || rowIdx} className="hover:bg-slate-50/80 transition-colors">
              {columns.map((col, colIdx) => (
                <td key={col.key || colIdx} className={`px-4 py-3.5 align-middle ${col.className || ''}`}>
                  {col.render ? col.render(row, rowIdx) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
