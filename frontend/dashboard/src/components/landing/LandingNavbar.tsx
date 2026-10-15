import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, ArrowRight, Activity, Terminal } from 'lucide-react';

interface LandingNavbarProps {
  onOpenDemoDrawer?: () => void;
}

export const LandingNavbar: React.FC<LandingNavbarProps> = ({ onOpenDemoDrawer }) => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/85 backdrop-blur-md border-b border-slate-200/80 transition-all select-none">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-xs group-hover:bg-blue-700 transition-colors">
            <ShieldCheck className="w-5 h-5 text-white" strokeWidth={2.2} />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="font-display font-bold text-lg tracking-tight text-slate-900">
              Perimeter
            </span>
            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-blue-50 text-blue-700 border border-blue-200 font-semibold hidden sm:inline">
              v2.4 Inline
            </span>
          </div>
        </Link>

        {/* Section Anchors */}
        <div className="hidden md:flex items-center gap-7 text-xs font-medium text-slate-600">
          <a href="#iceberg" className="hover:text-blue-600 transition-colors">
            Route Discovery
          </a>
          <a href="#sandbox" className="hover:text-blue-600 transition-colors">
            Live BOLA Sandbox
          </a>
          <a href="#topology" className="hover:text-blue-600 transition-colors">
            Edge Topology
          </a>
          <a href="#architecture" className="hover:text-blue-600 transition-colors">
            Architecture Bento
          </a>
        </div>

        {/* Action CTAs */}
        <div className="flex items-center gap-3">
          {onOpenDemoDrawer && (
            <button
              onClick={onOpenDemoDrawer}
              className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-amber-200 bg-amber-50/80 hover:bg-amber-100 text-amber-900 text-xs font-medium transition-all shadow-2xs"
            >
              <Terminal className="w-3.5 h-3.5 text-amber-700" strokeWidth={2} />
              <span>Simulate Attack</span>
            </button>
          )}

          <Link
            to="/overview"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 active:scale-98 text-white text-xs font-semibold shadow-xs hover:shadow-md transition-all"
          >
            <Activity className="w-3.5 h-3.5 text-blue-200" strokeWidth={2} />
            <span>Launch Console</span>
            <ArrowRight className="w-3.5 h-3.5 text-blue-200" strokeWidth={2} />
          </Link>
        </div>
      </div>
    </nav>
  );
};
