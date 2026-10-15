import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileCode,
  AlertTriangle,
  Skull,
  HelpCircle,
  ArrowRight,
  ShieldAlert,
  Layers,
  CheckCircle,
} from 'lucide-react';

interface DiscoveredRoute {
  id: string;
  method: string;
  path: string;
  status: 'documented' | 'shadow' | 'zombie' | 'unmanaged';
  trafficPct: string;
  riskScore: number;
  sensitivePii: string[];
  diffNote: string;
  callsPerMin: number;
}

const SAMPLE_ROUTES: DiscoveredRoute[] = [
  {
    id: 'r-1',
    method: 'GET',
    path: '/api/v2/users/me/profile',
    status: 'documented',
    trafficPct: '65%',
    riskScore: 12,
    sensitivePii: ['email'],
    diffNote: 'Fully conforms to openapi.yaml schema v2.4',
    callsPerMin: 1420,
  },
  {
    id: 'r-2',
    method: 'POST',
    path: '/api/v2/payments/upi-transfer',
    status: 'documented',
    trafficPct: '65%',
    riskScore: 28,
    sensitivePii: ['account_id', 'upi_id'],
    diffNote: 'Payload matches schema; idempotency headers verified',
    callsPerMin: 890,
  },
  {
    id: 'r-3',
    method: 'GET',
    path: '/internal/debug/tokens',
    status: 'shadow',
    trafficPct: '20%',
    riskScore: 98,
    sensitivePii: ['PAN', 'Aadhaar', 'Bearer Token'],
    diffNote: 'Undocumented debug route exposed on public ingress',
    callsPerMin: 340,
  },
  {
    id: 'r-4',
    method: 'POST',
    path: '/api/v1/admin/bypass-kyc',
    status: 'shadow',
    trafficPct: '20%',
    riskScore: 94,
    sensitivePii: ['Aadhaar', 'Phone'],
    diffNote: 'Direct internal bypass route absent from registered catalog',
    callsPerMin: 112,
  },
  {
    id: 'r-5',
    method: 'GET',
    path: '/v1/legacy/export/customers.csv',
    status: 'zombie',
    trafficPct: '5%',
    riskScore: 89,
    sensitivePii: ['PAN', 'Aadhaar', 'Salary'],
    diffNote: 'Deprecated in Q2 2024 but still receiving active caller traffic',
    callsPerMin: 45,
  },
  {
    id: 'r-6',
    method: 'POST',
    path: '/webhook/partner/unverified-callback',
    status: 'unmanaged',
    trafficPct: '10%',
    riskScore: 82,
    sensitivePii: ['Merchant Key', 'Secret'],
    diffNote: 'Third-party ingress without mutual TLS or bearer validation',
    callsPerMin: 210,
  },
];

export const RouteDiscoveryIceberg: React.FC = () => {
  const [selectedStatus, setSelectedStatus] = useState<'documented' | 'shadow' | 'zombie' | 'unmanaged'>('shadow');
  const [selectedRoute, setSelectedRoute] = useState<DiscoveredRoute>(
    SAMPLE_ROUTES.find((r) => r.status === 'shadow') || SAMPLE_ROUTES[0]
  );

  const filteredRoutes = SAMPLE_ROUTES.filter((r) => r.status === selectedStatus);

  const categories = [
    {
      id: 'documented' as const,
      name: 'Documented APIs',
      share: '65% of traffic',
      desc: 'Officially declared in openapi.yaml',
      icon: FileCode,
      color: 'text-emerald-700 bg-emerald-50 border-emerald-200',
      activeTab: 'bg-emerald-600 text-white',
    },
    {
      id: 'shadow' as const,
      name: 'Shadow APIs',
      share: '20% of traffic',
      desc: 'Active live routes missing from specifications',
      icon: AlertTriangle,
      color: 'text-amber-700 bg-amber-50 border-amber-200',
      activeTab: 'bg-amber-600 text-white',
    },
    {
      id: 'zombie' as const,
      name: 'Zombie APIs',
      share: '5% of traffic',
      desc: 'Deprecated endpoints forgotten in code',
      icon: Skull,
      color: 'text-rose-700 bg-rose-50 border-rose-200',
      activeTab: 'bg-rose-600 text-white',
    },
    {
      id: 'unmanaged' as const,
      name: 'Unmanaged / Partner',
      share: '10% of traffic',
      desc: 'External partner callbacks lacking telemetry',
      icon: HelpCircle,
      color: 'text-slate-700 bg-slate-100 border-slate-300',
      activeTab: 'bg-slate-800 text-white',
    },
  ];

  return (
    <section id="iceberg" className="py-24 bg-white border-b border-slate-200 select-none">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold mb-4">
            <Layers className="w-3.5 h-3.5 text-blue-600" />
            <span>CONTINUOUS PASSIVE SPEC SYNTHESIS</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-bold text-slate-900 tracking-tight mb-4">
            The API Route Discovery Iceberg
          </h2>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
            API documentation covers only what engineers remember to publish. Perimeter diffs live ingress traffic against registered contracts to instantly surface the submerged 35% of your attack surface.
          </p>
        </div>

        {/* Iceberg Category Tabs */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-10">
          {categories.map((cat) => {
            const Icon = cat.icon;
            const isSelected = selectedStatus === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => {
                  setSelectedStatus(cat.id);
                  const first = SAMPLE_ROUTES.find((r) => r.status === cat.id);
                  if (first) setSelectedRoute(first);
                }}
                className={`p-4 rounded-xl border text-left transition-all ${
                  isSelected
                    ? 'border-blue-600 bg-blue-50/40 shadow-sm ring-1 ring-blue-600'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center border ${cat.color}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-[11px] font-mono font-bold text-slate-500">{cat.share}</span>
                </div>
                <div className="text-sm font-semibold text-slate-900">{cat.name}</div>
                <div className="text-xs text-slate-500 mt-1 line-clamp-1">{cat.desc}</div>
              </button>
            );
          })}
        </div>

        {/* Interactive Master-Detail Explorer */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 rounded-2xl bg-slate-50 border border-slate-200 p-4 sm:p-6 shadow-sm">
          {/* Left: Filtered Routes List (5 cols) */}
          <div className="lg:col-span-5 space-y-2.5">
            <div className="flex items-center justify-between px-1 pb-2 border-b border-slate-200 text-xs font-semibold text-slate-700">
              <span>Detected Endpoints ({filteredRoutes.length})</span>
              <span className="font-mono text-slate-500 text-[11px]">Wire Frequency</span>
            </div>

            <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
              {filteredRoutes.map((route) => {
                const isSelected = selectedRoute.id === route.id;
                return (
                  <div
                    key={route.id}
                    onClick={() => setSelectedRoute(route)}
                    className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-white border-blue-600 shadow-sm'
                        : 'bg-white/80 border-slate-200 hover:border-slate-300 hover:bg-white'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${
                          route.method === 'GET' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-sky-50 text-sky-700 border-sky-200'
                        }`}>
                          {route.method}
                        </span>
                        <span className="font-mono text-xs font-medium text-slate-900 truncate max-w-[200px]">
                          {route.path}
                        </span>
                      </div>
                      <span className={`text-[10px] font-mono font-bold px-1.5 py-0.2 rounded border ${
                        route.riskScore > 80 ? 'bg-red-50 text-red-700 border-red-200' : 'bg-slate-100 text-slate-600 border-slate-200'
                      }`}>
                        Risk {route.riskScore}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono mt-2">
                      <span>{route.callsPerMin} req/min</span>
                      <span className="text-slate-400 truncate max-w-[150px]">{route.sensitivePii.join(', ')}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Right: Route Telemetry & Drift Inspector (7 cols) */}
          <div className="lg:col-span-7 bg-white border border-slate-200 rounded-xl p-5 flex flex-col justify-between shadow-2xs">
            <div>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-2">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-mono text-xs font-bold">
                      {selectedRoute.method}
                    </span>
                    <span className="font-mono text-sm font-semibold text-slate-900 truncate">
                      {selectedRoute.path}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 font-medium">
                    Endpoint Telemetry & Contract Synchronization
                  </div>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-center">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${
                    selectedRoute.status === 'documented'
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                      : 'bg-amber-50 text-amber-800 border-amber-200'
                  }`}>
                    {selectedRoute.status.toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Forensic Details Grid */}
              <div className="grid grid-cols-2 gap-4 my-5">
                <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/80">
                  <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
                    Exposed Sensitive PII
                  </div>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {selectedRoute.sensitivePii.map((pii) => (
                      <span
                        key={pii}
                        className="px-2 py-0.5 rounded bg-white text-rose-700 border border-rose-200 font-mono text-[11px] font-semibold shadow-2xs"
                      >
                        {pii}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200/80">
                  <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
                    Risk Assessment Formula
                  </div>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="text-2xl font-bold font-mono text-slate-900">
                      {selectedRoute.riskScore}
                    </span>
                    <span className="text-xs text-slate-500">/ 100 composite</span>
                  </div>
                </div>
              </div>

              {/* Schema Contract Diff */}
              <div className="p-4 rounded-xl bg-slate-900 text-slate-100 font-mono text-xs overflow-x-auto shadow-inner">
                <div className="text-[11px] text-slate-400 pb-2 border-b border-slate-800 flex justify-between">
                  <span>SPECIFICATION DIFF REPORT</span>
                  <span className="text-amber-400 font-semibold">{selectedRoute.diffNote}</span>
                </div>
                <div className="pt-3 space-y-1">
                  <p className="text-slate-400">// Registered openapi.yaml</p>
                  <p className="text-rose-400">- path: {selectedRoute.status === 'documented' ? selectedRoute.path : 'None (404 Missing in Spec)'}</p>
                  <p className="text-slate-400 mt-2">// Observed Wire Gateway Ingress</p>
                  <p className="text-emerald-400">+ path: {selectedRoute.path}</p>
                  <p className="text-emerald-400">+ payload_tokens: [{selectedRoute.sensitivePii.join(', ')}]</p>
                  <p className="text-sky-400">+ caller_frequency: {selectedRoute.callsPerMin} requests/minute</p>
                </div>
              </div>
            </div>

            {/* Action Bar */}
            <div className="pt-5 border-t border-slate-100 flex items-center justify-between mt-5">
              <span className="text-xs text-slate-500 flex items-center gap-1.5 font-medium">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                <span>Deterministic Identity Graph Synchronized</span>
              </span>

              <Link
                to="/inventory"
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 font-semibold text-xs transition-colors"
              >
                <span>Inspect in API Catalog</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
