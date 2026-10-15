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
          className={`inline-flex items-center text-[11px] font-medium px-1.5 py-0.5 rounded-[4px] border border-[#B47AEA]/30 text-[#B47AEA] bg-[#B47AEA]/10 dark:text-[#B47AEA] dark:border-[#B47AEA]/30 ${className}`}
        >
          Shadow
        </span>
      );
    case 'zombie':
      return (
        <span
          className={`inline-flex items-center text-[11px] font-medium px-1.5 py-0.5 rounded-[4px] border border-[#E5484D]/30 text-[#E5484D] bg-[#E5484D]/10 ${className}`}
        >
          Zombie
        </span>
      );
    case 'unmanaged':
      return (
        <span
          className={`inline-flex items-center text-[11px] font-medium px-1.5 py-0.5 rounded-[4px] border border-[#F76B15]/30 text-[#F76B15] bg-[#F76B15]/10 ${className}`}
        >
          Unmanaged
        </span>
      );
    case 'unused_documented':
      return (
        <span
          className={`inline-flex items-center text-[11px] font-medium px-1.5 py-0.5 rounded-[4px] border border-[#8B929C]/30 text-[#8B929C] bg-[#8B929C]/10 ${className}`}
        >
          Unused spec
        </span>
      );
    case 'documented':
    default:
      return (
        <span
          className={`inline-flex items-center text-[11px] font-medium px-1.5 py-0.5 rounded-[4px] border border-[#252A31] text-[#8B929C] bg-transparent ${className}`}
        >
          Documented
        </span>
      );
  }
};
