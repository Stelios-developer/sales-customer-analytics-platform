import React from 'react';
import { STATUS_COLORS } from '../utils/constants';

interface StatusBadgeProps {
  status: string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const color = STATUS_COLORS[status?.toLowerCase()] || '#6b7280';
  return (
    <span
      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
      style={{ backgroundColor: `${color}20`, color: color, border: `1px solid ${color}40` }}
    >
      {status}
    </span>
  );
}
