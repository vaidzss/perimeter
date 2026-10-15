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
        return 'text-[#8B929C] border-[#252A31] dark:text-[#8B929C] dark:border-[#252A31]';
      case 'POST':
        return 'text-[#4C8DFF] border-[#4C8DFF]/40 dark:text-[#4C8DFF] dark:border-[#4C8DFF]/30';
      case 'PUT':
        return 'text-[#E5A100] border-[#E5A100]/40 dark:text-[#E5A100] dark:border-[#E5A100]/30';
      case 'DELETE':
        return 'text-[#E5484D] border-[#E5484D]/40 dark:text-[#E5484D] dark:border-[#E5484D]/30';
      case 'PATCH':
        return 'text-[#B47AEA] border-[#B47AEA]/40 dark:text-[#B47AEA] dark:border-[#B47AEA]/30';
      default:
        return 'text-[#8B929C] border-[#252A31]';
    }
  };

  return (
    <span
      className={`inline-block font-mono text-[11px] px-1.5 py-0.5 rounded-[4px] border ${getStyle()} font-medium tracking-tight ${className}`}
    >
      {m}
    </span>
  );
};
