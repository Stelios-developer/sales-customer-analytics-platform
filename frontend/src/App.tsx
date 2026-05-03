import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import SalesAnalysis from './pages/SalesAnalysis';
import Orders from './pages/Orders';
import Customers from './pages/Customers';
import Products from './pages/Products';
import CustomerSegmentation from './pages/CustomerSegmentation';
import SalesForecasting from './pages/SalesForecasting';
import UploadDataset from './pages/UploadDataset';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="sales" element={<SalesAnalysis />} />
          <Route path="orders" element={<Orders />} />
          <Route path="customers" element={<Customers />} />
          <Route path="products" element={<Products />} />
          <Route path="segments" element={<CustomerSegmentation />} />
          <Route path="forecast" element={<SalesForecasting />} />
          <Route path="upload" element={<UploadDataset />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
