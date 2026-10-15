import React from 'react';
import { apiClient } from '../../api/client';

interface FooterProps {
  onOpenDemoDrawer: () => void;
}

export const Footer: React.FC<FooterProps> = ({ onOpenDemoDrawer }) => {
  const useMock = apiClient.getUseMock();

  return (
    <footer className="h-9 border-t border-slate-200 bg-white px-5 flex items-center justify-between text-xs text-slate-500 select-none shrink-0 font-mono">
      <div className="flex items-center gap-3">
        <span className="flex items-center gap-1.5 font-medium text-slate-800">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          <span>Polling: 1.5s Live Telemetry</span>
        </span>
        <span className="text-slate-300">·</span>
        <span className="text-slate-600">48,210 frames verified</span>
        <span className="text-slate-300">·</span>
        <span className="text-slate-600">Gateway Port 8000</span>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onOpenDemoDrawer}
          className="hover:text-slate-900 transition-colors flex items-center gap-1.5 text-slate-600"
        >
          <span className={`w-1.5 h-1.5 rounded-full ${useMock ? 'bg-amber-500' : 'bg-emerald-500'}`} />
          <span>Stream: {useMock ? 'Mock Telemetry' : 'Live Ingress Engine'}</span>
          <kbd className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-600 shadow-2xs">
            Shift+D
          </kbd>
        </button>
      </div>
    </footer>
  );
};
