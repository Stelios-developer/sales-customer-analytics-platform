import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import DataTable from '../components/DataTable';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { Customer } from '../types';

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        setLoading(true);
        setError(false);
        const params: Record<string, string> = {};
        if (search) params.search = search;
        const res = await apiClient.get('/customers', { params });
        setCustomers(res.data);
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    fetchCustomers();
  }, [search]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState />;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Customers</h2>

      <div className="bg-white p-4 rounded-xl border border-gray-200">
        <input
          type="text"
          placeholder="Search customers..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-full max-w-md"
        />
      </div>

      {customers.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-12">No customers found.</p>
      ) : (
        <DataTable headers={['Code', 'Name', 'Email', 'Country', 'City', 'Segment']}>
          {customers.map((c) => (
            <tr key={c.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 font-medium">{c.customer_code}</td>
              <td className="px-4 py-3">{c.first_name} {c.last_name}</td>
              <td className="px-4 py-3 text-gray-500">{c.email || '-'}</td>
              <td className="px-4 py-3">{c.country}</td>
              <td className="px-4 py-3">{c.city}</td>
              <td className="px-4 py-3">
                {c.segment ? (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700">
                    {c.segment}
                  </span>
                ) : (
                  '-'
                )}
              </td>
            </tr>
          ))}
        </DataTable>
      )}
    </div>
  );
}
