import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-gray-500">
      <Loader2 className="w-8 h-8 animate-spin mb-3" />
      <p className="text-sm">Loading data...</p>
    </div>
  );
}
