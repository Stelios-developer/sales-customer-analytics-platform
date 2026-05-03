import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import DataTable from '../components/DataTable';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import { Product } from '../types';
import { formatCurrency } from '../utils/formatters';

export default function Products() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [categories, setCategories] = useState<string[]>([]);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        setError(false);
        const params: Record<string, string> = {};
        if (search) params.search = search;
        if (category) params.category = category;
        const [pRes, cRes] = await Promise.all([
          apiClient.get('/products', { params }),
          apiClient.get('/products/categories'),
        ]);
        setProducts(pRes.data);
        setCategories(cRes.data);
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    fetchProducts();
  }, [search, category]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState />;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Products</h2>

      <div className="flex flex-wrap gap-3 bg-white p-4 rounded-xl border border-gray-200">
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm min-w-[200px]"
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      {products.length === 0 ? (
        <p className="text-sm text-gray-500 text-center py-12">No products found.</p>
      ) : (
        <DataTable headers={['Code', 'Name', 'Category', 'Unit Price', 'Cost Price']}>
          {products.map((p) => (
            <tr key={p.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 font-medium">{p.product_code}</td>
              <td className="px-4 py-3">{p.name}</td>
              <td className="px-4 py-3">{p.category}</td>
              <td className="px-4 py-3">{formatCurrency(p.unit_price)}</td>
              <td className="px-4 py-3">{formatCurrency(p.cost_price)}</td>
            </tr>
          ))}
        </DataTable>
      )}
    </div>
  );
}
