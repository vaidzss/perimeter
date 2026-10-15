import React from 'react';

interface MethodTagProps {
  method: string;
  className?: string;
}

export const MethodTag: React.FC<MethodTagProps> = ({ method, className = '' }) => {
  const m = method.toUpperCase();

  const getStyle = () => {
    switch (m) {
      case 'GET':
        return 'text-emerald-700 border-emerald-200 bg-emerald-50';
      case 'POST':
        return 'text-sky-700 border-sky-200 bg-sky-50';
      case 'PUT':
      case 'PATCH':
        return 'text-amber-700 border-amber-200 bg-amber-50';
      case 'DELETE':
        return 'text-rose-700 border-rose-200 bg-rose-50';
      default:
        return 'text-slate-700 border-slate-200 bg-slate-100';
    }
  };

  return (
    <span
      className={`inline-block font-mono text-[10.5px] px-2 py-0.5 rounded-md border ${getStyle()} font-semibold tracking-tight ${className}`}
    >
      {m}
    </span>
  );
};
