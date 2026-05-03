import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface ErrorStateProps {
  message?: string;
}

export default function ErrorState({ message = 'Failed to load data. Please try again.' }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-red-600">
      <AlertTriangle className="w-8 h-8 mb-3" />
      <p className="text-sm font-medium">{message}</p>
    </div>
  );
}
