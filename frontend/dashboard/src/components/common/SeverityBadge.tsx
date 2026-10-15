import React from 'react';
import { SeverityDot } from './SeverityDot';
import { AlertSeverity } from '../../types';

interface SeverityBadgeProps {
  severity: AlertSeverity;
  size?: 'sm' | 'md';
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({ severity }) => {
  return <SeverityDot severity={severity} />;
};
