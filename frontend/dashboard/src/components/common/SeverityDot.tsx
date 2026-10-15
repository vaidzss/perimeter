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
          dotColor: 'bg-[#E5484D]',
          textColor: 'text-[#E5484D]',
          label: 'Critical',
        };
      case 'high':
        return {
          dotColor: 'bg-[#F76B15]',
          textColor: 'text-[#F76B15]',
          label: 'High',
        };
      case 'medium':
        return {
          dotColor: 'bg-[#E5A100]',
          textColor: 'text-[#E5A100]',
          label: 'Medium',
        };
      case 'informational':
        return {
          dotColor: 'bg-[#4C8DFF]',
          textColor: 'text-[#4C8DFF]',
          label: 'Informational',
        };
      case 'low':
      default:
        return {
          dotColor: 'bg-[#8B929C]',
          textColor: 'text-[#8B929C]',
          label: 'Low',
        };
    }
  })();

  return (
    <span className={`inline-flex items-center gap-1.5 text-[12px] font-normal ${className}`}>
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${config.dotColor}`} />
      {showLabel && <span className={config.textColor}>{config.label}</span>}
    </span>
  );
};
