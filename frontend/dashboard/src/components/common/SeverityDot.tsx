import React from 'react';
import { AlertSeverity } from '../../types';

interface SeverityDotProps {
  severity: AlertSeverity | string;
  showLabel?: boolean;
  className?: string;
}

export const SeverityDot: React.FC<SeverityDotProps> = ({
  severity,
  showLabel = true,
  className = '',
}) => {
  const norm = severity.toLowerCase();

  const config = (() => {
    switch (norm) {
      case 'critical':
        return {
          dotColor: 'bg-red-600',
          textColor: 'text-red-700',
          badgeBg: 'bg-red-50 border-red-200',
          label: 'Critical',
        };
      case 'high':
        return {
          dotColor: 'bg-amber-600',
          textColor: 'text-amber-800',
          badgeBg: 'bg-amber-50 border-amber-200',
          label: 'High',
        };
      case 'medium':
        return {
          dotColor: 'bg-yellow-600',
          textColor: 'text-yellow-800',
          badgeBg: 'bg-yellow-50 border-yellow-200',
          label: 'Medium',
        };
      case 'informational':
        return {
          dotColor: 'bg-sky-600',
          textColor: 'text-sky-800',
          badgeBg: 'bg-sky-50 border-sky-200',
          label: 'Informational',
        };
      case 'low':
      default:
        return {
          dotColor: 'bg-slate-500',
          textColor: 'text-slate-700',
          badgeBg: 'bg-slate-100 border-slate-200',
          label: 'Low',
        };
    }
  })();

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border text-[11px] font-semibold ${config.badgeBg} ${config.textColor} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${config.dotColor}`} />
      {showLabel && <span>{config.label}</span>}
    </span>
  );
};
