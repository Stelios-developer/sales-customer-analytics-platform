export interface KPIData {
  total_revenue: number;
  total_profit: number;
  number_of_orders: number;
  number_of_customers: number;
  number_of_products: number;
  average_order_value: number;
  conversion_proxy: number;
  paid_revenue: number;
  pending_revenue: number;
  top_product: string | null;
  top_customer: string | null;
  best_country: string | null;
}

export interface MonthlySales {
  month: string;
  revenue: number;
  profit: number;
  orders: number;
}

export interface TopProduct {
  product_id: number;
  product_name: string;
  category: string;
  quantity_sold: number;
  revenue: number;
  profit: number;
}

export interface TopCustomer {
  customer_id: number;
  customer_name: string;
  country: string;
  orders: number;
  total_spent: number;
  average_order_value: number;
}

export interface SalesByCountry {
  country: string;
  revenue: number;
  orders: number;
  customers: number;
}

export interface SalesByCategory {
  category: string;
  revenue: number;
  profit: number;
  orders: number;
  quantity_sold: number;
}

export interface PaymentMethod {
  payment_method: string;
  total: number;
  count: number;
}

export interface OrderStatusSummary {
  status: string;
  count: number;
  revenue: number;
}

export interface ProfitSummary {
  total_revenue: number;
  total_cost: number;
  total_profit: number;
  profit_margin_pct: number;
}

export interface RecentOrder {
  order_id: number;
  order_number: string;
  customer_name: string;
  total_amount: number;
  status: string;
  order_date: string;
}

export interface Order {
  id: number;
  order_number: string;
  customer_id: number;
  customer_name: string;
  order_date: string;
  status: string;
  total_amount: number;
  discount_amount: number;
  shipping_amount: number;
  country: string;
  city: string;
  payment_status: string;
  payment_method: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface Customer {
  id: number;
  customer_code: string;
  first_name: string;
  last_name: string;
  email: string;
  country: string;
  city: string;
  segment: string | null;
  created_at: string;
}

export interface Product {
  id: number;
  product_code: string;
  name: string;
  category: string;
  unit_price: number;
  cost_price: number;
}

export interface ForecastPoint {
  date: string;
  predicted_revenue: number;
}

export interface TrainForecastResult {
  model_name: string;
  mae: number;
  rmse: number;
  r2: number;
  training_rows: number;
}

export interface TrainSegmentationResult {
  model_name: string;
  n_components: number;
  covariance_type: string;
  silhouette_score: number | null;
  aic: number | null;
  bic: number | null;
  training_rows: number;
}

export interface CustomerSegment {
  customer_id: number;
  customer_name: string;
  segment: string;
  recency_days: number;
  frequency: number;
  monetary_value: number;
}

export interface SegmentSummary {
  segment: string;
  count: number;
  avg_monetary_value: number;
  avg_frequency: number;
  avg_recency_days: number;
}

export interface ImportResult {
  status: string;
  filename: string;
  rows_processed: number;
  rows_inserted: number;
  rows_failed: number;
  warnings: string[];
  errors: string[];
}
