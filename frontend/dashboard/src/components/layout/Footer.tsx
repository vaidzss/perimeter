import React from 'react';
import { apiClient } from '../../api/client';
import { ShieldCheck, Activity } from 'lucide-react';

interface FooterProps {
  onOpenDemoDrawer: () => void;
}

export const Footer: React.FC<FooterProps> = ({ onOpenDemoDrawer }) => {
  const useMock = apiClient.getUseMock();

  return (
    <footer className="h-7 border-t border-[#252A31] bg-[#0E1013] px-4 flex items-center justify-between text-[11px] text-[#8B929C] select-none shrink-0 font-sans">
      <div className="flex items-center gap-3">
        <span className="flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
          <span>Updated 2s ago</span>
        </span>
        <span className="text-[#343B45]">·</span>
        <span className="font-mono text-[11px]">48,210 requests analyzed in active window</span>
        <span className="text-[#343B45]">·</span>
        <span>Scope: team-built test API ingress</span>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={onOpenDemoDrawer}
          className="hover:text-[#E6E8EB] transition-colors flex items-center gap-1.5"
        >
          <span className={`w-1.5 h-1.5 rounded-full ${useMock ? 'bg-[#E5A100]' : 'bg-[#10b981]'}`} />
          <span>Source: {useMock ? 'Mock fixtures' : 'FastAPI Live'}</span>
          <kbd className="text-[9px] font-mono px-1 py-0.2 rounded bg-[#15181D] border border-[#252A31]">Shift+D</kbd>
        </button>
      </div>
    </footer>
  );
};
