import React from 'react';
import { ApiInventoryStatus } from '../../types';

interface StatusTagProps {
  status: ApiInventoryStatus | string;
  className?: string;
}

export const StatusTag: React.FC<StatusTagProps> = ({ status, className = '' }) => {
  const norm = status.toLowerCase();

  switch (norm) {
    case 'shadow':
      return (
        <span
          className={`inline-flex items-center text-[11px] font-semibold px-2 py-0.5 rounded-md border border-amber-200 text-amber-800 bg-amber-50 ${className}`}
        >
          Shadow
        </span>
      );
    case 'zombie':
      return (
        <span
          className={`inline-flex items-center text-[11px] font-semibold px-2 py-0.5 rounded-md border border-rose-200 text-rose-800 bg-rose-50 ${className}`}
        >
          Zombie
        </span>
      );
    case 'unmanaged':
      return (
        <span
          className={`inline-flex items-center text-[11px] font-semibold px-2 py-0.5 rounded-md border border-sky-200 text-sky-800 bg-sky-50 ${className}`}
        >
          Unmanaged
        </span>
      );
    case 'unused_documented':
      return (
        <span
          className={`inline-flex items-center text-[11px] font-medium px-2 py-0.5 rounded-md border border-slate-200 text-slate-600 bg-slate-50 ${className}`}
        >
          Unused Spec
        </span>
      );
    case 'documented':
    default:
      return (
        <span
          className={`inline-flex items-center text-[11px] font-medium px-2 py-0.5 rounded-md border border-emerald-200 text-emerald-800 bg-emerald-50 ${className}`}
        >
          Documented
        </span>
      );
  }
};
