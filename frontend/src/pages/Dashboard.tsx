import React, { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar,
} from 'recharts';
import { DollarSign, ShoppingBag, Users, Package, TrendingUp, Award, Globe } from 'lucide-react';
import apiClient from '../api/client';
import KPICard from '../components/KPICard';
import ChartCard from '../components/ChartCard';
import DataTable from '../components/DataTable';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';
import StatusBadge from '../components/StatusBadge';
import { KPIData, MonthlySales, SalesByCategory, SalesByCountry, TopProduct, RecentOrder } from '../types';
import { formatCurrency, formatNumber, formatMonth, formatDate } from '../utils/formatters';

const COLORS = ['#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f97316', '#84cc16'];

export default function Dashboard() {
  const [kpis, setKpis] = useState<KPIData | null>(null);
  const [monthly, setMonthly] = useState<MonthlySales[]>([]);
  const [categories, setCategories] = useState<SalesByCategory[]>([]);
  const [countries, setCountries] = useState<SalesByCountry[]>([]);
  const [topProducts, setTopProducts] = useState<TopProduct[]>([]);
  const [recentOrders, setRecentOrders] = useState<RecentOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        setLoading(true);
        setError(false);
        const [kpiRes, monthlyRes, catRes, countryRes, prodRes, orderRes] = await Promise.all([
          apiClient.get('/analytics/kpis'),
          apiClient.get('/analytics/monthly-sales'),
          apiClient.get('/analytics/sales-by-category'),
          apiClient.get('/analytics/sales-by-country'),
          apiClient.get('/analytics/top-products?limit=5'),
          apiClient.get('/analytics/recent-orders'),
        ]);
        setKpis(kpiRes.data);
        setMonthly(monthlyRes.data);
        setCategories(catRes.data);
        setCountries(countryRes.data);
        setTopProducts(prodRes.data);
        setRecentOrders(orderRes.data);
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState />;
  if (!kpis) return <ErrorState message="No data available." />;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Dashboard Overview</h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Total Revenue" value={formatCurrency(kpis.total_revenue)} icon={<DollarSign size={20} />} color="emerald" />
        <KPICard title="Total Profit" value={formatCurrency(kpis.total_profit)} icon={<TrendingUp size={20} />} color="indigo" />
        <KPICard title="Orders" value={formatNumber(kpis.number_of_orders)} icon={<ShoppingBag size={20} />} color="amber" />
        <KPICard title="Customers" value={formatNumber(kpis.number_of_customers)} icon={<Users size={20} />} color="sky" />
        <KPICard title="Avg Order Value" value={formatCurrency(kpis.average_order_value)} icon={<DollarSign size={20} />} color="rose" />
        <KPICard title="Products Sold" value={formatNumber(kpis.number_of_products)} icon={<Package size={20} />} color="emerald" />
        <KPICard title="Top Product" value={kpis.top_product || '-'} icon={<Award size={20} />} color="amber" />
        <KPICard title="Best Country" value={kpis.best_country || '-'} icon={<Globe size={20} />} color="indigo" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Monthly Revenue & Profit">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tickFormatter={formatMonth} />
              <YAxis tickFormatter={(v) => `$${v}`} />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Legend />
              <Line type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="profit" stroke="#22c55e" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Sales by Category">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categories}
                dataKey="revenue"
                nameKey="category"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={(entry) => entry.category}
              >
                {categories.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Top Products">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topProducts} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" tickFormatter={(v) => `$${v}`} />
              <YAxis dataKey="product_name" type="category" width={120} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Bar dataKey="revenue" fill="#6366f1" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Sales by Country">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={countries}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="country" />
              <YAxis tickFormatter={(v) => `$${v}`} />
              <Tooltip formatter={(value: number) => formatCurrency(value)} />
              <Bar dataKey="revenue" fill="#22c55e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard title="Recent Orders">
        {recentOrders.length === 0 ? (
          <p className="text-sm text-gray-500 py-8 text-center">No recent orders found.</p>
        ) : (
          <DataTable headers={['Order', 'Customer', 'Amount', 'Status', 'Date']}>
            {recentOrders.map((o) => (
              <tr key={o.order_id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{o.order_number}</td>
                <td className="px-4 py-3">{o.customer_name}</td>
                <td className="px-4 py-3">{formatCurrency(o.total_amount)}</td>
                <td className="px-4 py-3"><StatusBadge status={o.status} /></td>
                <td className="px-4 py-3 text-gray-500">{formatDate(o.order_date)}</td>
              </tr>
            ))}
          </DataTable>
        )}
      </ChartCard>
    </div>
  );
}
