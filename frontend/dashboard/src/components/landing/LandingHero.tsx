import React from 'react';
import { Link } from 'react-router-dom';
import { InteractiveMeshCanvas } from './InteractiveMeshCanvas';
import {
  ShieldAlert,
  ArrowRight,
  Terminal,
  Zap,
  Lock,
  Cpu,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';

interface LandingHeroProps {
  onOpenDemoDrawer?: () => void;
}

export const LandingHero: React.FC<LandingHeroProps> = ({ onOpenDemoDrawer }) => {
  return (
    <section className="relative pt-32 pb-20 md:pt-40 md:pb-32 overflow-hidden bg-[#FAFAFA] border-b border-slate-200">
      {/* Background Interactive Topological Particle Mesh */}
      <InteractiveMeshCanvas className="opacity-70" />

      {/* Subtle radial accent gradient for soft warmth */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[720px] h-[360px] bg-gradient-to-b from-blue-100/30 via-slate-100/20 to-transparent blur-3xl pointer-events-none -z-10" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
        <div className="text-center max-w-4xl mx-auto">
          {/* Live Telemetry Pill */}
          <div className="hero-pill inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white border border-slate-200 shadow-2xs text-[11px] font-mono mb-8">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
            </span>
            <span className="font-semibold text-slate-800">WIRE-SPEED INLINE PROTECTION</span>
            <span className="text-slate-300">·</span>
            <span className="text-blue-700 font-bold">&lt;1.2ms OVERHEAD</span>
            <span className="text-slate-300">·</span>
            <span className="text-slate-500">0.0% FALSE POSITIVE GUARANTEE</span>
          </div>

          {/* High-Impact Editorial Headline */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-slate-900 leading-[1.08] mb-6">
            <span className="hero-title-line block">Your API Gateway Sees Traffic.</span>
            <span className="hero-title-line block text-transparent bg-clip-text bg-gradient-to-r from-blue-700 via-blue-800 to-slate-900">
              Perimeter Sees the Threat.
            </span>
          </h1>

          {/* Sub-headline */}
          <p className="hero-subtitle text-lg sm:text-xl text-slate-600 font-normal leading-relaxed max-w-2xl mx-auto mb-10">
            Zero-day BOLA detection, shadow route discovery, and inline virtual patching at wire speed — without touching application code.
          </p>

          {/* Primary & Secondary Action CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-3 sm:gap-4 mb-16">
            <Link
              to="/overview"
              className="hero-cta-btn inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 active:scale-98 text-white font-semibold text-sm shadow-sm hover:shadow-md transition-all group"
            >
              <span>Open Security Console</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </Link>

            <a
              href="#sandbox"
              className="hero-cta-btn inline-flex items-center gap-2 px-5 py-3.5 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 hover:border-slate-300 active:scale-98 text-slate-800 font-semibold text-sm shadow-2xs transition-all"
            >
              <Terminal className="w-4 h-4 text-slate-600" />
              <span>Explore Live Sandbox</span>
            </a>

            {onOpenDemoDrawer && (
              <button
                onClick={onOpenDemoDrawer}
                className="hero-cta-btn inline-flex items-center gap-2 px-4 py-3.5 rounded-xl bg-amber-50 hover:bg-amber-100 border border-amber-200 text-amber-900 font-semibold text-sm transition-all shadow-2xs"
              >
                <Zap className="w-4 h-4 text-amber-700" />
                <span>Simulate Attack (Shift+D)</span>
              </button>
            )}
          </div>

          {/* Architecture Trust Highlights Strip */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto text-left text-xs text-slate-600 font-medium">
            <div className="flex items-center gap-2.5 p-3 rounded-xl bg-white/70 border border-slate-200/80 shadow-2xs">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>Zero App Code Changes</span>
            </div>
            <div className="flex items-center gap-2.5 p-3 rounded-xl bg-white/70 border border-slate-200/80 shadow-2xs">
              <Lock className="w-4 h-4 text-blue-600 shrink-0" />
              <span>DPDP & RBI PII Masking</span>
            </div>
            <div className="flex items-center gap-2.5 p-3 rounded-xl bg-white/70 border border-slate-200/80 shadow-2xs">
              <Cpu className="w-4 h-4 text-sky-600 shrink-0" />
              <span>Native Envoy Rust Filter</span>
            </div>
            <div className="flex items-center gap-2.5 p-3 rounded-xl bg-white/70 border border-slate-200/80 shadow-2xs">
              <ShieldAlert className="w-4 h-4 text-rose-600 shrink-0" />
              <span>OWASP Top 10 API Guard</span>
            </div>
          </div>
        </div>

        {/* Live Interactive Telemetry Showcase Card */}
        <div className="hero-canvas-card mt-14 max-w-5xl mx-auto rounded-2xl bg-white border border-slate-200 p-4 sm:p-6 shadow-xl relative">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-red-400" />
              <div className="w-3 h-3 rounded-full bg-amber-400" />
              <div className="w-3 h-3 rounded-full bg-emerald-400" />
              <span className="text-xs font-mono text-slate-400 ml-2">
                perimeter-edge-envoy :: live wire inspection buffer
              </span>
            </div>
            <div className="flex items-center gap-2 font-mono text-[11px] text-slate-500">
              <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold">
                ENFORCING
              </span>
              <span>Proxy Port 8000</span>
            </div>
          </div>

          {/* Dual Threat & Discovery Live Signals */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5">
            {/* Signal 1: Real-time BOLA blocked */}
            <div className="p-4 rounded-xl bg-rose-50/70 border border-rose-200/90 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="px-2 py-0.5 rounded bg-rose-100 text-rose-800 text-[10px] font-mono font-bold">
                    BLOCKED · BOLA / IDOR
                  </span>
                  <span className="text-[11px] font-mono text-rose-700">0.8ms wire drop</span>
                </div>
                <div className="font-mono text-xs font-semibold text-rose-950 truncate">
                  GET /accounts/10892/statement
                </div>
                <p className="text-xs text-rose-800/80 mt-1.5 leading-relaxed">
                  Actor <code className="font-mono bg-white px-1 py-0.5 rounded text-rose-900 border border-rose-200">u_anon_882</code> attempted cross-tenant object harvest. Object ownership mismatch detected via Identity Graph.
                </p>
              </div>
              <div className="mt-3 pt-2 border-t border-rose-200/60 flex items-center justify-between text-[11px] font-mono text-rose-700">
                <span>Verdict: 403 Forbidden</span>
                <span className="font-semibold">Inline Virtual Patch Active</span>
              </div>
            </div>

            {/* Signal 2: Shadow Route Identified */}
            <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200/90 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="px-2 py-0.5 rounded bg-amber-100 text-amber-800 text-[10px] font-mono font-bold">
                    DRIFT · SHADOW ROUTE
                  </span>
                  <span className="text-[11px] font-mono text-amber-700">Contract Diff Alert</span>
                </div>
                <div className="font-mono text-xs font-semibold text-amber-950 truncate">
                  POST /internal/debug/tokens
                </div>
                <p className="text-xs text-amber-800/80 mt-1.5 leading-relaxed">
                  Undocumented route discovered in live traffic. Sensitive payload contains <span className="font-semibold text-amber-900">Aadhaar, PAN & Bearer Token</span>.
                </p>
              </div>
              <div className="mt-3 pt-2 border-t border-amber-200/60 flex items-center justify-between text-[11px] font-mono text-amber-700">
                <span>Spec Status: Not in openapi.yaml</span>
                <span className="font-semibold">Quarantine Available</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
