import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import DataTable from '../components/DataTable';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import StatusBadge from '../components/StatusBadge';
import { Order, PaginatedResponse } from '../types';
import { formatCurrency, formatDate } from '../utils/formatters';

export default function Orders() {
  const [data, setData] = useState<PaginatedResponse<Order>>({ items: [], total: 0, page: 1, page_size: 20, pages: 1 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [country, setCountry] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const fetchOrders = async (page = 1) => {
    try {
      setLoading(true);
      setError(false);
      const params: Record<string, string | number> = { page, page_size: 20 };
      if (search) params.search = search;
      if (status) params.status = status;
      if (country) params.country = country;
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;
      const res = await apiClient.get('/orders', { params });
      setData(res.data);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const applyFilters = (e: React.FormEvent) => {
    e.preventDefault();
    fetchOrders(1);
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState />;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Orders</h2>

      <form onSubmit={applyFilters} className="flex flex-wrap gap-3 items-end bg-white p-4 rounded-xl border border-gray-200">
        <input
          type="text"
          placeholder="Search orders..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm min-w-[200px]"
        />
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
        >
          <option value="">All Statuses</option>
          <option value="completed">Completed</option>
          <option value="pending">Pending</option>
          <option value="shipped">Shipped</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <input
          type="text"
          placeholder="Country"
          value={country}
          onChange={(e) => setCountry(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
        />
        <input
          type="date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
        />
        <input
          type="date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
        />
        <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700">
          Filter
        </button>
      </form>

      {data.items.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-12">No orders found.</p>
      ) : (
        <>
          <DataTable headers={['Order', 'Customer', 'Total', 'Status', 'Country', 'Date']}>
            {data.items.map((o) => (
              <tr key={o.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{o.order_number}</td>
                <td className="px-4 py-3">{o.customer_name}</td>
                <td className="px-4 py-3">{formatCurrency(o.total_amount)}</td>
                <td className="px-4 py-3"><StatusBadge status={o.status} /></td>
                <td className="px-4 py-3">{o.country}</td>
                <td className="px-4 py-3 text-gray-500">{formatDate(o.order_date)}</td>
              </tr>
            ))}
          </DataTable>

          <div className="flex items-center justify-between text-sm text-gray-600">
            <p>
              Showing {data.items.length} of {data.total} orders (Page {data.page} of {data.pages})
            </p>
            <div className="flex gap-2">
              <button
                disabled={data.page <= 1}
                onClick={() => fetchOrders(data.page - 1)}
                className="px-3 py-1 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                Previous
              </button>
              <button
                disabled={data.page >= data.pages}
                onClick={() => fetchOrders(data.page + 1)}
                className="px-3 py-1 border border-gray-300 rounded-lg disabled:opacity-50 hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
