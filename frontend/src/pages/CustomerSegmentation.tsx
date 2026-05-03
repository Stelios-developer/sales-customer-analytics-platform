import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import apiClient from '../api/client';
import ChartCard from '../components/ChartCard';
import DataTable from '../components/DataTable';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { CustomerSegment, SegmentSummary, TrainSegmentationResult } from '../types';
import { formatCurrency } from '../utils/formatters';

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

export default function CustomerSegmentation() {
  const [customers, setCustomers] = useState<CustomerSegment[]>([]);
  const [summary, setSummary] = useState<SegmentSummary[]>([]);
  const [metrics, setMetrics] = useState<TrainSegmentationResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState(false);
  const [message, setMessage] = useState('');

  const fetchSegments = async () => {
    try {
      setLoading(true);
      setError(false);
      setMessage('');
      const res = await apiClient.get('/ml/customer-segments');
      if (res.data.status === 'no_model' || res.data.status === 'insufficient_data') {
        setMessage(res.data.message || 'No segmentation model available.');
        setCustomers([]);
        setSummary([]);
      } else {
        setCustomers(res.data.customers);
        setSummary(res.data.summary);
      }
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  const trainModel = async () => {
    try {
      setTraining(true);
      setMessage('');
      const res = await apiClient.post('/ml/train-segmentation');
      if (res.data.status === 'insufficient_data') {
        setMessage(res.data.message);
      } else {
        setMetrics(res.data);
        setMessage(`${res.data.model_name} segmentation model trained successfully!`);
        await fetchSegments();
      }
    } catch {
      setMessage('Failed to train segmentation model.');
    } finally {
      setTraining(false);
    }
  };

  useEffect(() => {
    fetchSegments();
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Customer Segmentation</h2>
        <button
          onClick={trainModel}
          disabled={training}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
        >
          {training ? 'Training...' : 'Train Segmentation Model'}
        </button>
      </div>

      {message && (
        <div className="bg-amber-50 text-amber-800 px-4 py-3 rounded-lg text-sm border border-amber-200">
          {message}
        </div>
      )}

      {metrics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <p className="text-sm text-gray-500">Model</p>
            <p className="mt-1 text-lg font-bold text-gray-900">{metrics.model_name}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <p className="text-sm text-gray-500">Components</p>
            <p className="mt-1 text-lg font-bold text-gray-900">{metrics.n_components}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <p className="text-sm text-gray-500">Silhouette</p>
            <p className="mt-1 text-lg font-bold text-gray-900">
              {metrics.silhouette_score === null ? 'N/A' : metrics.silhouette_score.toFixed(2)}
            </p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <p className="text-sm text-gray-500">BIC</p>
            <p className="mt-1 text-lg font-bold text-gray-900">
              {metrics.bic === null ? 'N/A' : metrics.bic.toFixed(0)}
            </p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">About RFM Features</h3>
        <p className="text-sm text-gray-600">
          Segments are derived from a <strong>Gaussian Mixture Model</strong> trained on <strong>RFM analysis</strong>: <strong>Recency</strong> (days since last order),
          <strong> Frequency</strong> (number of orders), and <strong>Monetary Value</strong> (total spent).
          These dimensions identify your highest-value, loyal, at-risk, and low-activity customers.
        </p>
      </div>

      {customers.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartCard title="Segment Distribution">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={summary}
                  dataKey="count"
                  nameKey="segment"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {summary.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Segment Summary">
            <DataTable headers={['Segment', 'Count', 'Avg Spend', 'Avg Freq', 'Avg Recency']}>
              {summary.map((s) => (
                <tr key={s.segment} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{s.segment}</td>
                  <td className="px-4 py-3">{s.count}</td>
                  <td className="px-4 py-3">{formatCurrency(s.avg_monetary_value)}</td>
                  <td className="px-4 py-3">{s.avg_frequency.toFixed(1)}</td>
                  <td className="px-4 py-3">{s.avg_recency_days.toFixed(0)} days</td>
                </tr>
              ))}
            </DataTable>
          </ChartCard>
        </div>
      )}

      {customers.length > 0 && (
        <ChartCard title="Customer Segments">
          <DataTable headers={['Customer', 'Segment', 'Recency', 'Frequency', 'Monetary Value']}>
            {customers.map((c) => (
              <tr key={c.customer_id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{c.customer_name}</td>
                <td className="px-4 py-3">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700">
                    {c.segment}
                  </span>
                </td>
                <td className="px-4 py-3">{c.recency_days} days</td>
                <td className="px-4 py-3">{c.frequency}</td>
                <td className="px-4 py-3">{formatCurrency(c.monetary_value)}</td>
              </tr>
            ))}
          </DataTable>
        </ChartCard>
      )}
    </div>
  );
}
