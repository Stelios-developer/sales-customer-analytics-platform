export const formatCurrency = (value: number | null | undefined): string => {
  if (value == null || Number.isNaN(value)) return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
};

export const formatNumber = (value: number | null | undefined): string => {
  if (value == null || Number.isNaN(value)) return '0';
  return new Intl.NumberFormat('en-US').format(value);
};

export const formatDate = (value: string | null | undefined): string => {
  if (!value) return '-';
  return new Date(value).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const formatMonth = (value: string | null | undefined): string => {
  if (!value) return '-';
  const [year, month] = value.split('-');
  const date = new Date(Number(year), Number(month) - 1);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
};
