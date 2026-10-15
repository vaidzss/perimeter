import React from 'react';
import { StatusTag } from './StatusTag';
import { ApiInventoryStatus } from '../../types';

interface StatusBadgeProps {
  status: ApiInventoryStatus;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  return <StatusTag status={status} />;
};
