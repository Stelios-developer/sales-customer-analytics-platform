import React from 'react';

interface DataTableProps {
  headers: string[];
  children: React.ReactNode;
}

export default function DataTable({ headers, children }: DataTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
      <table className="w-full text-sm text-left">
        <thead className="bg-gray-50 text-gray-600 font-medium">
          <tr>
            {headers.map((h) => (
              <th key={h} className="px-4 py-3 border-b border-gray-200 whitespace-nowrap">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {children}
        </tbody>
      </table>
    </div>
  );
}
