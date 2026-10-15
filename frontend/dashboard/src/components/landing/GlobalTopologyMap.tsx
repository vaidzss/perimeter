import React, { useState } from 'react';
import { Globe, Radio, Activity, ShieldCheck, Server, Zap } from 'lucide-react';

interface EdgePop {
  id: string;
  name: string;
  city: string;
  role: string;
  xPct: number;
  yPct: number;
  latencyMs: number;
  throughputRps: number;
  blockedExploits: number;
  activePatches: number;
  port: number;
  status: 'optimal' | 'armed';
}

const EDGE_POPS: EdgePop[] = [
  {
    id: 'mumbai',
    name: 'Mumbai Ingress Hub',
    city: 'Mumbai, IN',
    role: 'Primary Gateway & TLS Termination',
    xPct: 67,
    yPct: 56,
    latencyMs: 4.2,
    throughputRps: 18420,
    blockedExploits: 148,
    activePatches: 6,
    port: 8000,
    status: 'optimal',
  },
  {
    id: 'delhi',
    name: 'Delhi Core Mesh',
    city: 'New Delhi, IN',
    role: 'Protected Banking Mesh & DB Cluster',
    xPct: 69,
    yPct: 46,
    latencyMs: 6.1,
    throughputRps: 14100,
    blockedExploits: 92,
    activePatches: 4,
    port: 8001,
    status: 'armed',
  },
  {
    id: 'singapore',
    name: 'Singapore Edge POP',
    city: 'Singapore, SG',
    role: 'APAC Ingress & Bot Mitigation',
    xPct: 78,
    yPct: 64,
    latencyMs: 22.5,
    throughputRps: 9800,
    blockedExploits: 67,
    activePatches: 3,
    port: 8000,
    status: 'optimal',
  },
  {
    id: 'frankfurt',
    name: 'Frankfurt Mirror',
    city: 'Frankfurt, DE',
    role: 'EMEA Partner Gateway & Safe Mirror',
    xPct: 49,
    yPct: 37,
    latencyMs: 41.0,
    throughputRps: 5890,
    blockedExploits: 28,
    activePatches: 2,
    port: 8000,
    status: 'optimal',
  },
];

export const GlobalTopologyMap: React.FC = () => {
  const [selectedPop, setSelectedPop] = useState<EdgePop>(EDGE_POPS[0]);

  return (
    <section id="topology" className="py-24 bg-white border-b border-slate-200 select-none">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-50 border border-sky-200 text-sky-800 text-xs font-semibold mb-4">
            <Globe className="w-3.5 h-3.5 text-sky-600" />
            <span>GLOBAL EDGE DEFENSE TOPOLOGY</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-bold text-slate-900 tracking-tight mb-4">
            Distributed Wire-Speed Telemetry
          </h2>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
            Perimeter's lightweight Envoy filters deploy directly to edge POPs and private VPC gateways. Continuous telemetry is aggregated with zero latency penalty on upstream core services.
          </p>
        </div>

        {/* Global Map Canvas & Telemetry Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 rounded-2xl bg-[#F8FAFC] border border-slate-200 p-4 sm:p-6 shadow-sm">
          {/* Left: Vector Map Canvas (8 cols) */}
          <div className="lg:col-span-8 bg-white border border-slate-200 rounded-xl p-5 relative overflow-hidden shadow-2xs min-h-[380px] flex flex-col justify-between">
            {/* Top Bar inside Map */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 z-10">
              <div className="flex items-center gap-2 font-mono text-xs text-slate-600">
                <Radio className="w-3.5 h-3.5 text-blue-600 animate-pulse" />
                <span>4 Active Edge POPs Verified</span>
              </div>
              <span className="text-[11px] font-mono text-emerald-700 font-semibold bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                Total Fleet: 48,210 RPS
              </span>
            </div>

            {/* Interactive Vector Map Surface */}
            <div className="relative flex-1 w-full my-6 min-h-[260px] flex items-center justify-center">
              {/* Subtle map coordinate gridlines */}
              <div className="absolute inset-0 bg-grid-light opacity-50" />

              {/* Connecting Topology Arcs SVG */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                <defs>
                  <linearGradient id="routeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#2563EB" stopOpacity="0.4" />
                    <stop offset="100%" stopColor="#0284C7" stopOpacity="0.4" />
                  </linearGradient>
                </defs>

                {/* Frankfurt -> Mumbai Arc */}
                <path
                  d="M 390 120 Q 480 140 530 180"
                  stroke="url(#routeGrad)"
                  strokeWidth="1.5"
                  strokeDasharray="4 4"
                  fill="none"
                />
                {/* Mumbai -> Delhi Arc */}
                <path
                  d="M 530 180 Q 540 160 550 148"
                  stroke="#2563EB"
                  strokeWidth="2"
                  fill="none"
                />
                {/* Mumbai -> Singapore Arc */}
                <path
                  d="M 530 180 Q 580 200 620 205"
                  stroke="url(#routeGrad)"
                  strokeWidth="1.5"
                  strokeDasharray="4 4"
                  fill="none"
                />
              </svg>

              {/* POP Nodes */}
              {EDGE_POPS.map((pop) => {
                const isSelected = selectedPop.id === pop.id;
                return (
                  <div
                    key={pop.id}
                    onClick={() => setSelectedPop(pop)}
                    style={{ left: `${pop.xPct}%`, top: `${pop.yPct}%` }}
                    className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-20"
                  >
                    <div className="relative flex items-center justify-center">
                      {/* Pulse Ring */}
                      <span className={`absolute inline-flex h-7 w-7 rounded-full opacity-40 transition-all ${
                        isSelected ? 'bg-blue-600 animate-ping' : 'bg-slate-400 group-hover:scale-125'
                      }`} />
                      
                      {/* Core Node Dot */}
                      <span className={`relative inline-flex rounded-full h-4 w-4 border-2 transition-all ${
                        isSelected
                          ? 'bg-blue-600 border-white shadow-md scale-110'
                          : 'bg-white border-blue-600 group-hover:border-slate-800'
                      }`} />
                    </div>

                    {/* Node Hover Tooltip Label */}
                    <div className={`mt-1.5 px-2 py-0.5 rounded-md text-[10.5px] font-mono whitespace-nowrap transition-all shadow-2xs ${
                      isSelected
                        ? 'bg-slate-900 text-white font-bold'
                        : 'bg-white/90 text-slate-700 border border-slate-200 group-hover:bg-slate-900 group-hover:text-white'
                    }`}>
                      {pop.city} · {pop.latencyMs}ms
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Bottom Latency Legend */}
            <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between text-xs text-slate-500 font-mono">
              <div className="flex items-center gap-4">
                <span>Core: Envoy Rust Inline</span>
                <span>Wire TLS: OpenSSL 3.0</span>
              </div>
              <span className="text-blue-600 font-semibold">Click any edge POP to inspect</span>
            </div>
          </div>

          {/* Right: Edge POP Telemetry Card (4 cols) */}
          <div className="lg:col-span-4 bg-white border border-slate-200 rounded-xl p-5 flex flex-col justify-between shadow-2xs">
            <div>
              <div className="pb-4 border-b border-slate-100">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-bold text-blue-600 uppercase tracking-wider">
                    {selectedPop.role}
                  </span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                    STATUS: {selectedPop.status.toUpperCase()}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mt-1">{selectedPop.name}</h3>
                <p className="text-xs text-slate-500 mt-0.5">{selectedPop.city}</p>
              </div>

              {/* Metrics Counters */}
              <div className="space-y-3.5 my-5">
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                  <span className="text-xs text-slate-600 font-medium">Throughput</span>
                  <span className="font-mono text-base font-bold text-slate-900">
                    {selectedPop.throughputRps.toLocaleString()} <span className="text-xs font-normal text-slate-500">req/s</span>
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                  <span className="text-xs text-slate-600 font-medium">Median Wire Latency</span>
                  <span className="font-mono text-base font-bold text-blue-600">
                    {selectedPop.latencyMs} <span className="text-xs font-normal text-slate-500">ms</span>
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                  <span className="text-xs text-slate-600 font-medium">Neutralized Exploits</span>
                  <span className="font-mono text-base font-bold text-rose-600">
                    {selectedPop.blockedExploits} <span className="text-xs font-normal text-slate-500">blocked</span>
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 flex items-center justify-between">
                  <span className="text-xs text-slate-600 font-medium">Active Virtual Patches</span>
                  <span className="font-mono text-base font-bold text-amber-600">
                    {selectedPop.activePatches} <span className="text-xs font-normal text-slate-500">traps</span>
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-mono">
              <span>Binding: Port {selectedPop.port}</span>
              <span className="text-emerald-700 font-semibold flex items-center gap-1">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>Zero Drops</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
