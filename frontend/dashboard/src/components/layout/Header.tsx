import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Search, SlidersHorizontal, Radio, ExternalLink } from 'lucide-react';

interface HeaderProps {
  onOpenCommandPalette: () => void;
  onOpenDemoDrawer: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenCommandPalette, onOpenDemoDrawer }) => {
  return (
    <header className="h-14 bg-white/90 backdrop-blur-md border-b border-slate-200 px-5 flex items-center justify-between text-xs text-slate-900 select-none sticky top-0 z-40">
      {/* Left: Product Brand & Fleet Operation Status */}
      <div className="flex items-center gap-4">
        <Link to="/overview" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 bg-blue-600 text-white rounded-xl flex items-center justify-center group-hover:bg-blue-700 transition-all shadow-xs">
            <ShieldCheck className="w-5 h-5 text-white" strokeWidth={2.2} />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="font-display font-bold text-base tracking-tight text-slate-900">
              Perimeter
            </span>
            <span className="text-[11px] font-mono text-slate-500 hidden sm:inline">
              Command Center
            </span>
          </div>
        </Link>

        <div className="h-4 w-px bg-slate-200" />

        {/* Live Defense Status Badge */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-[11px] font-medium shadow-2xs">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
          </span>
          <span>Active Ingress Guard</span>
        </div>

        {/* Environment Selector Pill */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-50 border border-slate-200 text-slate-600 text-[11px]">
          <Radio className="w-3 h-3 text-sky-600" />
          <span>Fleet:</span>
          <span className="text-slate-900 font-semibold">BharatPay Core Production</span>
        </div>
      </div>

      {/* Center: Command Palette Trigger */}
      <button
        onClick={onOpenCommandPalette}
        className="flex items-center justify-between gap-3 px-3.5 py-1.5 bg-slate-50 border border-slate-200 hover:border-slate-300 hover:bg-slate-100 text-slate-500 hover:text-slate-800 rounded-xl text-xs transition-all w-52 sm:w-72 shadow-2xs"
      >
        <div className="flex items-center gap-2 truncate">
          <Search className="w-3.5 h-3.5 text-slate-400" strokeWidth={2} />
          <span className="truncate">Search API endpoints, tokens, actors...</span>
        </div>
        <kbd className="text-[10px] px-1.5 py-0.5 rounded bg-white border border-slate-200 text-slate-600 font-mono shadow-2xs">
          ⌘K
        </kbd>
      </button>

      {/* Right: Quick Controls & SecOps Profile */}
      <div className="flex items-center gap-3">
        {/* Public Landing Link */}
        <Link
          to="/"
          className="hidden xl:flex items-center gap-1.5 px-2.5 py-1.5 text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-100 text-xs font-medium transition-colors"
          title="Return to Product Showcase Landing"
        >
          <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
          <span>Landing Page</span>
        </Link>

        {/* Simulate scenario drawer trigger */}
        <button
          onClick={onOpenDemoDrawer}
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 border border-amber-200 hover:border-amber-300 bg-amber-50 hover:bg-amber-100 text-amber-900 rounded-xl text-xs font-medium transition-all shadow-2xs"
          title="Simulate Red-Team Attack Scenarios [Shift+D]"
        >
          <SlidersHorizontal className="w-3.5 h-3.5 text-amber-700" strokeWidth={2} />
          <span>Simulate Red-Team</span>
          <kbd className="text-[9.5px] px-1 py-0.2 rounded bg-white border border-amber-200 text-amber-800 font-mono shadow-2xs">
            ⇧D
          </kbd>
        </button>

        {/* Operator Profile */}
        <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center font-mono text-xs font-bold text-slate-700 shadow-2xs">
            SO
          </div>
        </div>
      </div>
    </header>
  );
};
