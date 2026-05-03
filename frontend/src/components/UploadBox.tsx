import React, { useState, useCallback } from 'react';
import { UploadCloud } from 'lucide-react';

interface UploadBoxProps {
  onFileSelect: (file: File) => void;
  uploading: boolean;
}

export default function UploadBox({ onFileSelect, uploading }: UploadBoxProps) {
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  }, [onFileSelect]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      className={`
        relative border-2 border-dashed rounded-xl p-10 text-center transition-colors cursor-pointer
        ${dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 bg-white hover:border-gray-400'}
      `}
    >
      <input
        type="file"
        accept=".csv"
        onChange={handleChange}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
      <div className="flex flex-col items-center gap-3">
        <div className="p-3 bg-indigo-50 rounded-full">
          <UploadCloud className="w-8 h-8 text-indigo-600" />
        </div>
        <p className="text-sm font-medium text-gray-700">
          {uploading ? 'Uploading...' : 'Drag & drop a CSV file here, or click to browse'}
        </p>
        <p className="text-xs text-gray-500">Supported format: .csv (max 100MB)</p>
      </div>
    </div>
  );
}
