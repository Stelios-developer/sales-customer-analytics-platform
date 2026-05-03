import React, { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar,
} from 'recharts';
import apiClient from '../api/client';
import ChartCard from '../components/ChartCard';
import DataTable from '../components/DataTable';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { MonthlySales, PaymentMethod, OrderStatusSummary, SalesByCountry, SalesByCategory } from '../types';
import { formatCurrency, formatMonth } from '../utils/formatters';

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#84cc16'];

export default function SalesAnalysis() {
  const [monthly, setMonthly] = useState<MonthlySales[]>([]);
  const [payments, setPayments] = useState<PaymentMethod[]>([]);
  const [statuses, setStatuses] = useState<OrderStatusSummary[]>([]);
  const [countries, setCountries] = useState<SalesByCountry[]>([]);
  const [categories, setCategories] = useState<SalesByCategory[]>([]);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(false);
      const params: Record<string, string> = {};
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;

      const [mRes, pRes, sRes, cRes, catRes] = await Promise.all([
        apiClient.get('/analytics/monthly-sales', { params }),
        apiClient.get('/analytics/payment-methods', { params }),
        apiClient.get('/analytics/order-status', { params }),
        apiClient.get('/analytics/sales-by-country', { params }),
        apiClient.get('/analytics/sales-by-category', { params }),
      ]);
      setMonthly(mRes.data);
      setPayments(pRes.data);
      setStatuses(sRes.data);
      setCountries(cRes.data);
      setCategories(catRes.data);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const applyFilters = (e: React.FormEvent) => {
    e.preventDefault();
    fetchData();
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Sales Analysis</h2>
      </div>

      <form onSubmit={applyFilters} className="flex flex-wrap gap-3 items-end bg-white p-4 rounded-xl border border-gray-200">
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">From</label>
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">To</label>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <button
          type="submit"
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700"
        >
          Apply Filters
        </button>
      </form>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Revenue Trend">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tickFormatter={formatMonth} />
              <YAxis tickFormatter={(v) => `$${v}`} />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Legend />
              <Line type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Profit Trend">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tickFormatter={formatMonth} />
              <YAxis tickFormatter={(v) => `$${v}`} />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Legend />
              <Line type="monotone" dataKey="profit" stroke="#22c55e" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Payment Methods">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={payments} dataKey="total" nameKey="payment_method" cx="50%" cy="50%" outerRadius={90} label>
                {payments.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Order Status">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={statuses} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={90} label>
                {statuses.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Country Breakdown">
          {countries.length === 0 ? (
            <p className="text-sm text-gray-500 py-8 text-center">No data available.</p>
          ) : (
            <DataTable headers={['Country', 'Revenue', 'Orders', 'Customers']}>
              {countries.map((c) => (
                <tr key={c.country} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{c.country}</td>
                  <td className="px-4 py-3">{formatCurrency(c.revenue)}</td>
                  <td className="px-4 py-3">{c.orders}</td>
                  <td className="px-4 py-3">{c.customers}</td>
                </tr>
              ))}
            </DataTable>
          )}
        </ChartCard>

        <ChartCard title="Category Breakdown">
          {categories.length === 0 ? (
            <p className="text-sm text-gray-500 py-8 text-center">No data available.</p>
          ) : (
            <DataTable headers={['Category', 'Revenue', 'Profit', 'Orders']}>
              {categories.map((c) => (
                <tr key={c.category} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{c.category}</td>
                  <td className="px-4 py-3">{formatCurrency(c.revenue)}</td>
                  <td className="px-4 py-3">{formatCurrency(c.profit)}</td>
                  <td className="px-4 py-3">{c.orders}</td>
                </tr>
              ))}
            </DataTable>
          )}
        </ChartCard>
      </div>
    </div>
  );
}
