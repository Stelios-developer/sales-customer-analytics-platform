import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import apiClient from '../api/client';
import ChartCard from '../components/ChartCard';
import DataTable from '../components/DataTable';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { ForecastPoint, TrainForecastResult } from '../types';
import { formatCurrency } from '../utils/formatters';

export default function SalesForecasting() {
  const [forecast, setForecast] = useState<ForecastPoint[]>([]);
  const [metrics, setMetrics] = useState<TrainForecastResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState(false);
  const [message, setMessage] = useState('');

  const fetchForecast = async () => {
    try {
      setLoading(true);
      setError(false);
      setMessage('');
      const res = await apiClient.get('/ml/sales-forecast');
      if (res.data.status === 'no_model' || res.data.status === 'insufficient_data') {
        setMessage(res.data.message || 'Forecast not available.');
        setForecast([]);
      } else {
        setForecast(res.data.forecast);
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
      const res = await apiClient.post('/ml/train-forecast');
      if (res.data.status === 'insufficient_data' || res.data.status === 'dependency_missing') {
        setMessage(res.data.message);
      } else {
        setMetrics(res.data);
        setMessage('Forecast model trained successfully!');
        await fetchForecast();
      }
    } catch {
      setMessage('Failed to train forecast model.');
    } finally {
      setTraining(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-900">Sales Forecasting</h2>
        <button
          onClick={trainModel}
          disabled={training}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
        >
          {training ? 'Training...' : 'Train Forecast Model'}
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
            <p className="text-sm text-gray-500">MAE</p>
            <p className="mt-1 text-lg font-bold text-gray-900">{formatCurrency(metrics.mae)}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <p className="text-sm text-gray-500">RMSE</p>
            <p className="mt-1 text-lg font-bold text-gray-900">{formatCurrency(metrics.rmse)}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
            <p className="text-sm text-gray-500">R² Score</p>
            <p className="mt-1 text-lg font-bold text-gray-900">{metrics.r2.toFixed(2)}</p>
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Model Limitations</h3>
        <p className="text-sm text-gray-600">
          The forecast uses XGBoost with daily calendar, lag, rolling-average, and order-volume features.
          Predictions assume similar business conditions; sudden market shifts, promotions, or seasonality
          not present in training data may reduce accuracy. Retrain regularly as new data arrives.
        </p>
      </div>

      {forecast.length > 0 && (
        <>
          <ChartCard title="30-Day Revenue Forecast">
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={forecast}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="date" />
                <YAxis tickFormatter={(v) => `$${v}`} />
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="predicted_revenue"
                  stroke="#6366f1"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  name="Predicted Revenue"
                />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Forecast Table">
            <DataTable headers={['Date', 'Predicted Revenue']}>
              {forecast.map((f) => (
                <tr key={f.date} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{f.date}</td>
                  <td className="px-4 py-3">{formatCurrency(f.predicted_revenue)}</td>
                </tr>
              ))}
            </DataTable>
          </ChartCard>
        </>
      )}
    </div>
  );
}
