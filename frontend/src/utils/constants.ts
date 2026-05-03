export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const STATUS_COLORS: Record<string, string> = {
  completed: '#22c55e',
  paid: '#22c55e',
  shipped: '#3b82f6',
  pending: '#f59e0b',
  failed: '#ef4444',
  cancelled: '#6b7280',
  refunded: '#8b5cf6',
};

export const PAGE_SIZES = [10, 20, 50, 100];
