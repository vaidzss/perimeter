import React, { useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  Play,
  RotateCcw,
  Zap,
  ArrowRight,
  Server,
  Network,
  CheckCircle2,
  XCircle,
} from 'lucide-react';

interface Scenario {
  id: string;
  name: string;
  type: string;
  request: {
    method: string;
    endpoint: string;
    headers: Record<string, string>;
    body?: string;
  };
  graphCheck: {
    actor: string;
    targetResource: string;
    relationship: string;
    verdict: string;
  };
  mitigatedResponse: {
    status: number;
    statusText: string;
    latency: string;
    headers: Record<string, string>;
    body: Record<string, any>;
  };
  unprotectedResponse: {
    status: number;
    statusText: string;
    latency: string;
    body: Record<string, any>;
  };
}

const SCENARIOS: Scenario[] = [
  {
    id: 'bola',
    name: 'BOLA / IDOR Account Harvest',
    type: 'OWASP API1:2023',
    request: {
      method: 'GET',
      endpoint: '/api/v2/merchants/8921/payout',
      headers: {
        Host: 'api.bharatpay.internal',
        Authorization: 'Bearer eyJhbGciOi... (sub: u_1042)',
        'X-Client-IP': '103.21.244.12 (Mumbai)',
      },
    },
    graphCheck: {
      actor: 'u_1042 (Standard Consumer)',
      targetResource: 'MerchantAccount(id=8921)',
      relationship: 'DISJOINT_TENANT (Zero ownership edge)',
      verdict: 'FAIL: Uncorrelated Resource Access',
    },
    mitigatedResponse: {
      status: 403,
      statusText: 'Forbidden',
      latency: '0.9ms',
      headers: {
        'x-perimeter-guard': 'ARMED',
        'x-mitigation-rule': 'VIRTUAL_PATCH_BOLA_AUTO_403',
        'x-identity-graph-ms': '0.3',
      },
      body: {
        error: 'BOLA_VIOLATION_PREVENTED',
        status: 403,
        detail: 'Caller identity does not possess ownership of target object id=8921',
        action: 'INLINE_BLOCK_EXECUTED',
      },
    },
    unprotectedResponse: {
      status: 200,
      statusText: 'OK',
      latency: '24.2ms',
      body: {
        merchant_id: 8921,
        account_name: 'Apex Logistics Pvt Ltd',
        payout_bank: 'HDFC0001234',
        balance_pnr: 4500000,
        pan_number: 'AAACP8921K',
        aadhaar_vault_ref: 'AV-9812-4411',
      },
    },
  },
  {
    id: 'token_replay',
    name: 'Concurrent Token Geo-Replay',
    type: 'OWASP API2:2023',
    request: {
      method: 'POST',
      endpoint: '/accounts/transfer',
      headers: {
        Host: 'api.bharatpay.internal',
        Authorization: 'Bearer tok_9918ab (sub: u_441)',
        'X-Client-IP': '194.135.22.4 (Frankfurt)',
      },
      body: JSON.stringify({ to: 'acc_771', amount: 50000, currency: 'INR' }, null, 2),
    },
    graphCheck: {
      actor: 'u_441 (Session active in Delhi 12s ago)',
      targetResource: 'High-Value UPI Transfer (50,000 INR)',
      relationship: 'GEO_VELOCITY_ANOMALY (8,400 km/min travel speed)',
      verdict: 'FAIL: Token Stolen / Concurrent Replay',
    },
    mitigatedResponse: {
      status: 401,
      statusText: 'Unauthorized',
      latency: '1.1ms',
      headers: {
        'x-perimeter-guard': 'ARMED',
        'x-mitigation-rule': 'TOKEN_REPLAY_FREEZE',
        'x-session-revoked': 'true',
      },
      body: {
        error: 'TOKEN_SPOOFING_DETECTED',
        status: 401,
        detail: 'Simultaneous session originating across impossible geographic distance',
        action: 'TOKEN_REVOKED_AND_QUARANTINED',
      },
    },
    unprotectedResponse: {
      status: 200,
      statusText: 'OK',
      latency: '38.0ms',
      body: {
        transfer_id: 'txn_982441',
        status: 'SUCCESS',
        amount_debited: 50000,
        compromised_wallet: 'acc_441',
      },
    },
  },
  {
    id: 'mass_assignment',
    name: 'Mass Assignment Privilege Escalation',
    type: 'OWASP API3:2023',
    request: {
      method: 'PUT',
      endpoint: '/api/v2/users/me',
      headers: {
        Host: 'api.bharatpay.internal',
        Authorization: 'Bearer eyJhbGciOi... (sub: u_908)',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: 'Rohit Sharma', role: 'superadmin', tier: 'internal_ops' }, null, 2),
    },
    graphCheck: {
      actor: 'u_908 (Tier: Standard Retail)',
      targetResource: 'UserEntity(id=908)',
      relationship: 'SCHEMA_VIOLATION (Forbidden write to [role, tier])',
      verdict: 'FAIL: Unauthorized Property Injection',
    },
    mitigatedResponse: {
      status: 400,
      statusText: 'Bad Request',
      latency: '0.8ms',
      headers: {
        'x-perimeter-guard': 'ARMED',
        'x-mitigation-rule': 'STRIP_FORBIDDEN_ATTRIBUTES',
      },
      body: {
        error: 'MASS_ASSIGNMENT_MUTATION_REJECTED',
        status: 400,
        detail: 'Attempted modification of protected contract attributes: role, tier',
        action: 'INLINE_REQUEST_SANITIZED',
      },
    },
    unprotectedResponse: {
      status: 200,
      statusText: 'OK',
      latency: '19.5ms',
      body: {
        user_id: 908,
        name: 'Rohit Sharma',
        role: 'superadmin',
        tier: 'internal_ops',
        elevated: true,
      },
    },
  },
];

export const LiveBolasandbox: React.FC = () => {
  const [activeScenario, setActiveScenario] = useState<Scenario>(SCENARIOS[0]);
  const [guardActive, setGuardActive] = useState<boolean>(true);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [simulationStep, setSimulationStep] = useState<number>(3); // 1 = Ingress, 2 = Graph Check, 3 = Mitigation Complete

  const triggerSimulation = () => {
    setIsRunning(true);
    setSimulationStep(1);

    setTimeout(() => {
      setSimulationStep(2);
      setTimeout(() => {
        setSimulationStep(3);
        setIsRunning(false);
      }, 500);
    }, 450);
  };

  return (
    <section id="sandbox" className="py-24 bg-[#F8FAFC] border-b border-slate-200 select-none">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold mb-4">
            <Zap className="w-3.5 h-3.5 text-emerald-600" />
            <span>INTERACTIVE WIRE ARBITRATION SANDBOX</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-bold text-slate-900 tracking-tight mb-4">
            Test the Inline BOLA Prevention Engine
          </h2>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
            Execute real-world authorization abuse payloads. Watch Perimeter's Deterministic Identity Graph evaluate tenant boundaries and enforce virtual patches at sub-millisecond wire speed.
          </p>
        </div>

        {/* Sandbox Console Container */}
        <div className="rounded-2xl bg-white border border-slate-200 shadow-xl overflow-hidden max-w-6xl mx-auto">
          {/* Top Control Bar */}
          <div className="p-4 sm:p-5 border-b border-slate-200 bg-slate-50/70 flex flex-col md:flex-row md:items-center justify-between gap-4">
            {/* Scenario Selector Pills */}
            <div className="flex flex-wrap items-center gap-2">
              {SCENARIOS.map((sc) => (
                <button
                  key={sc.id}
                  onClick={() => {
                    setActiveScenario(sc);
                    setSimulationStep(3);
                  }}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 ${
                    activeScenario.id === sc.id
                      ? 'bg-blue-600 text-white shadow-2xs'
                      : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <span>{sc.name}</span>
                  <span className={`text-[10px] font-mono px-1 rounded ${
                    activeScenario.id === sc.id ? 'bg-blue-700 text-blue-100' : 'bg-slate-100 text-slate-500'
                  }`}>
                    {sc.type.split(':')[0]}
                  </span>
                </button>
              ))}
            </div>

            {/* Guard Toggle & Run Action */}
            <div className="flex items-center gap-3">
              {/* Virtual Patch Guard Toggle */}
              <button
                onClick={() => setGuardActive(!guardActive)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border text-xs font-semibold transition-all ${
                  guardActive
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                    : 'bg-rose-50 text-rose-800 border-rose-300'
                }`}
              >
                {guardActive ? (
                  <>
                    <ShieldCheck className="w-4 h-4 text-emerald-600" />
                    <span>Perimeter Guard: Active</span>
                  </>
                ) : (
                  <>
                    <ShieldAlert className="w-4 h-4 text-rose-600" />
                    <span>Perimeter Guard: Disabled</span>
                  </>
                )}
              </button>

              {/* Run Attack Button */}
              <button
                onClick={triggerSimulation}
                disabled={isRunning}
                className="flex items-center gap-2 px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 active:scale-98 text-white font-semibold text-xs shadow-xs transition-all disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{isRunning ? 'Arbitrating...' : 'Execute Request'}</span>
              </button>
            </div>
          </div>

          {/* 3-Step Live Inspection Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 divide-y lg:divide-y-0 lg:divide-x divide-slate-200">
            {/* Step 1: Inbound Request (Wire) */}
            <div className="p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-slate-100 border border-slate-200 text-slate-600 text-[11px] font-mono font-bold flex items-center justify-center">
                      1
                    </span>
                    <span className="text-xs font-semibold text-slate-900">Wire Ingress Request</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                    simulationStep >= 1 ? 'bg-sky-50 text-sky-700 border border-sky-200' : 'text-slate-400'
                  }`}>
                    TLS Decoded
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-slate-900 text-white font-mono text-xs font-bold">
                      {activeScenario.request.method}
                    </span>
                    <span className="font-mono text-xs text-slate-800 font-semibold truncate">
                      {activeScenario.request.endpoint}
                    </span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-700 font-mono text-[11px] space-y-1 mt-3">
                    {Object.entries(activeScenario.request.headers).map(([k, v]) => (
                      <div key={k} className="truncate">
                        <span className="text-slate-400">{k}:</span> {v}
                      </div>
                    ))}
                    {activeScenario.request.body && (
                      <div className="pt-2 mt-2 border-t border-slate-200">
                        <span className="text-slate-400">// Request Body</span>
                        <pre className="text-slate-800 text-[10.5px] mt-0.5 leading-tight">
                          {activeScenario.request.body}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="mt-4 text-[11px] text-slate-500 font-mono flex items-center gap-1.5">
                <Network className="w-3.5 h-3.5 text-slate-400" />
                <span>Captured at Port 8000 Envoy</span>
              </div>
            </div>

            {/* Step 2: Deterministic Identity Graph Arbitration */}
            <div className="p-5 flex flex-col justify-between bg-slate-50/40">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-3">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-slate-100 border border-slate-200 text-slate-600 text-[11px] font-mono font-bold flex items-center justify-center">
                      2
                    </span>
                    <span className="text-xs font-semibold text-slate-900">Identity Graph Check</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                    simulationStep >= 2 ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'text-slate-400'
                  }`}>
                    0.3ms Resolution
                  </span>
                </div>

                <div className="space-y-3">
                  <div className="p-3 rounded-xl bg-white border border-slate-200 space-y-2 text-xs">
                    <div>
                      <div className="text-[10px] font-mono text-slate-400 uppercase">Authenticated Actor</div>
                      <div className="font-mono font-semibold text-slate-800 mt-0.5">
                        {activeScenario.graphCheck.actor}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] font-mono text-slate-400 uppercase">Target Resource Object</div>
                      <div className="font-mono font-semibold text-slate-800 mt-0.5">
                        {activeScenario.graphCheck.targetResource}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] font-mono text-slate-400 uppercase">Graph Relationship Edge</div>
                      <div className="font-mono font-bold text-rose-600 mt-0.5">
                        {activeScenario.graphCheck.relationship}
                      </div>
                    </div>
                  </div>

                  <div className={`p-3 rounded-xl border font-mono text-xs flex items-center gap-2.5 ${
                    guardActive
                      ? 'bg-rose-50 border-rose-200 text-rose-800'
                      : 'bg-amber-50 border-amber-200 text-amber-800'
                  }`}>
                    <XCircle className="w-4 h-4 shrink-0 text-rose-600" />
                    <div>
                      <div className="font-bold">{activeScenario.graphCheck.verdict}</div>
                      <div className="text-[10.5px] mt-0.5">
                        {guardActive ? 'Deterministic block triggered' : 'Bypassed (Guard turned off)'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 text-[11px] text-slate-500 font-mono flex items-center gap-1.5">
                <Server className="w-3.5 h-3.5 text-slate-400" />
                <span>0.0% False Positive Guarantee</span>
              </div>
            </div>

            {/* Step 3: Wire Verdict & Response */}
            <div className="p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-slate-100 border border-slate-200 text-slate-600 text-[11px] font-mono font-bold flex items-center justify-center">
                      3
                    </span>
                    <span className="text-xs font-semibold text-slate-900">Final Wire Verdict</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                    guardActive
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                      : 'bg-rose-50 text-rose-800 border border-rose-200'
                  }`}>
                    {guardActive ? activeScenario.mitigatedResponse.latency : activeScenario.unprotectedResponse.latency}
                  </span>
                </div>

                {guardActive ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-1 rounded bg-rose-600 text-white font-mono text-xs font-bold">
                        {activeScenario.mitigatedResponse.status} {activeScenario.mitigatedResponse.statusText}
                      </span>
                      <span className="text-xs font-semibold text-rose-700">Exploit Blocked Inline</span>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-900 text-slate-100 font-mono text-[11px] overflow-x-auto shadow-inner space-y-1">
                      <div className="text-slate-400">// Injected Mitigation Response</div>
                      <pre className="text-emerald-400 leading-tight">
                        {JSON.stringify(activeScenario.mitigatedResponse.body, null, 2)}
                      </pre>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-1 rounded bg-amber-600 text-white font-mono text-xs font-bold">
                        {activeScenario.unprotectedResponse.status} {activeScenario.unprotectedResponse.statusText}
                      </span>
                      <span className="text-xs font-semibold text-amber-700">Data Leakage Occurred!</span>
                    </div>

                    <div className="p-3 rounded-xl bg-rose-950/20 border border-rose-200 text-rose-900 font-mono text-[11px] overflow-x-auto space-y-1">
                      <div className="text-rose-700 font-semibold">// Customer Record Leaked:</div>
                      <pre className="text-rose-900 leading-tight">
                        {JSON.stringify(activeScenario.unprotectedResponse.body, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="font-mono text-slate-500 text-[11px]">
                  {guardActive ? 'Rule: Virtual Patch Active' : 'Unprotected Gateway Leak'}
                </span>
                <span className={`font-semibold flex items-center gap-1 ${
                  guardActive ? 'text-emerald-600' : 'text-rose-600'
                }`}>
                  {guardActive ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                  <span>{guardActive ? 'Safe' : 'Compromised'}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
