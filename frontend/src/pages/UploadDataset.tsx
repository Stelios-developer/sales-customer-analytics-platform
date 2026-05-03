import React, { useState } from 'react';
import apiClient from '../api/client';
import UploadBox from '../components/UploadBox';
import LoadingState from '../components/LoadingState';
import { ImportResult } from '../types';

const REQUIRED_COLUMNS = [
  'order_number', 'order_date', 'customer_code', 'customer_first_name',
  'customer_last_name', 'customer_email', 'customer_country', 'customer_city',
  'product_code', 'product_name', 'product_category', 'quantity',
  'unit_price', 'cost_price', 'discount_amount', 'shipping_amount',
  'payment_method', 'payment_status', 'payment_date', 'order_status',
];

export default function UploadDataset() {
  const [result, setResult] = useState<ImportResult | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const handleFileSelect = async (file: File) => {
    try {
      setUploading(true);
      setError('');
      setResult(null);
      const formData = new FormData();
      formData.append('file', file);
      const res = await apiClient.post('/imports/sales', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(res.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-3xl">
      <h2 className="text-xl font-bold text-gray-900">Upload Dataset</h2>

      <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm space-y-4">
        <h3 className="text-sm font-semibold text-gray-700">Supported CSV Format</h3>
        <p className="text-sm text-gray-600">
          Upload a single CSV file with denormalized sales rows. The system will normalize data into
          relational tables: customers, products, orders, order_items, and payments.
        </p>
        <div className="flex flex-wrap gap-2">
          {REQUIRED_COLUMNS.map((col) => (
            <span
              key={col}
              className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-700"
            >
              {col}
            </span>
          ))}
        </div>
      </div>

      <UploadBox onFileSelect={handleFileSelect} uploading={uploading} />

      {uploading && <LoadingState />}

      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg text-sm border border-red-200">
          {error}
        </div>
      )}

      {result && (
        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${result.status === 'success' ? 'bg-green-500' : 'bg-amber-500'}`}
            />
            <h3 className="text-sm font-semibold text-gray-700">Import Summary</h3>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500">Processed</p>
              <p className="text-lg font-bold text-gray-900">{result.rows_processed}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500">Inserted</p>
              <p className="text-lg font-bold text-gray-900">{result.rows_inserted}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500">Failed</p>
              <p className="text-lg font-bold text-gray-900">{result.rows_failed}</p>
            </div>
          </div>

          {result.warnings.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-medium text-amber-700">Warnings</p>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                {result.warnings.map((w, i) => (
                  <li key={i}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          {result.errors.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-medium text-red-700">Errors</p>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                {result.errors.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
