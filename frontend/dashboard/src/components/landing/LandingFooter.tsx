import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, ArrowRight, Activity, Terminal } from 'lucide-react';

export const LandingFooter: React.FC = () => {
  return (
    <footer className="bg-white border-t border-slate-200 select-none">
      {/* Pre-footer Call to Action */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center border-b border-slate-100">
        <div className="max-w-3xl mx-auto">
          <div className="w-12 h-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center mx-auto mb-6 shadow-md">
            <ShieldCheck className="w-7 h-7" strokeWidth={2.2} />
          </div>

          <h2 className="text-3xl sm:text-5xl font-bold text-slate-900 tracking-tight mb-4">
            Wire-Speed API Security. Zero Guesswork.
          </h2>
          <p className="text-base sm:text-lg text-slate-600 max-w-xl mx-auto mb-8 leading-relaxed">
            Protect your production services against zero-day BOLA, token hijacking, and shadow API exposure with deterministic precision.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3">
            <Link
              to="/overview"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 active:scale-98 text-white font-semibold text-sm shadow-sm hover:shadow-md transition-all"
            >
              <Activity className="w-4 h-4" />
              <span>Launch Security Console</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/evaluation"
              className="inline-flex items-center gap-2 px-5 py-3.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-800 font-semibold text-sm transition-all"
            >
              <Terminal className="w-4 h-4 text-slate-500" />
              <span>Inspect Benchmarks</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Main Footer Links & Status Ticker */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 pb-8 border-b border-slate-100 text-xs text-slate-600">
          {/* Logo & Operational Status */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 font-display font-bold text-slate-900 text-sm">
              <div className="w-6 h-6 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                <ShieldCheck className="w-4 h-4" strokeWidth={2.5} />
              </div>
              <span>Perimeter</span>
            </div>
            <span className="text-slate-300">·</span>
            <div className="flex items-center gap-1.5 font-mono text-emerald-700 font-medium bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>Fleet Status: All Edge POPs Operational</span>
            </div>
          </div>

          {/* Quick Links */}
          <div className="flex flex-wrap items-center gap-6 font-medium text-slate-600">
            <Link to="/overview" className="hover:text-blue-600 transition-colors">
              Console Overview
            </Link>
            <Link to="/inventory" className="hover:text-blue-600 transition-colors">
              API Inventory
            </Link>
            <Link to="/traffic" className="hover:text-blue-600 transition-colors">
              Traffic Telemetry
            </Link>
            <Link to="/alerts" className="hover:text-blue-600 transition-colors">
              Threat Alerts
            </Link>
            <Link to="/evaluation" className="hover:text-blue-600 transition-colors">
              Detection Benchmarks
            </Link>
          </div>
        </div>

        {/* Legal & Copyright */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400 font-mono">
          <div>
            © 2026 Perimeter Systems. Architectural Security & Identity Graph Engine.
          </div>
          <div className="flex items-center gap-4">
            <span>Envoy 1.30+ Compatible</span>
            <span>·</span>
            <span>FastAPI & Kubernetes Native</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
