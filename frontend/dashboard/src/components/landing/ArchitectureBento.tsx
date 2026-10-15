import React from 'react';
import {
  ShieldCheck,
  Zap,
  FileCode2,
  Lock,
  ArrowRight,
  Cpu,
  Layers,
  Database,
  CheckCircle,
} from 'lucide-react';

export const ArchitectureBento: React.FC = () => {
  return (
    <section id="architecture" className="py-24 bg-white border-b border-slate-200 select-none">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold mb-4">
            <Cpu className="w-3.5 h-3.5 text-blue-600" />
            <span>ENGINEERED FOR PRODUCTION BACKENDS</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-bold text-slate-900 tracking-tight mb-4">
            Deterministic API Defense Architecture
          </h2>
          <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
            Built from first principles for high-throughput banking and enterprise APIs. Perimeter replaces statistical guesswork with deterministic authorization graph verification.
          </p>
        </div>

        {/* Asymmetric 4-Card Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: 0.0% False Positive Guarantee (Span 2) */}
          <div className="md:col-span-2 p-7 rounded-2xl bg-[#F8FAFC] border border-slate-200 hover:border-slate-300 transition-all flex flex-col justify-between shadow-xs">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-200 text-blue-700 flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5" strokeWidth={2.2} />
                </div>
                <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                  0.0% FALSE POSITIVE GUARANTEE
                </span>
              </div>

              <h3 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                Deterministic Identity Graph Verification
              </h3>
              <p className="text-slate-600 text-sm sm:text-base mt-2 leading-relaxed max-w-xl">
                Traditional WAFs rely on regex signatures and heuristic statistical scores that trigger costly false positives on legitimate financial transactions. Perimeter maps the mathematical relationship between the <strong>authenticated subject</strong>, the <strong>resource ID</strong>, and the <strong>operation context</strong> directly from the data layer.
              </p>

              {/* Technical Architecture Callout Box */}
              <div className="mt-6 p-4 rounded-xl bg-white border border-slate-200 font-mono text-xs space-y-2">
                <div className="text-slate-400 font-semibold">// Identity Graph Constraint Verification</div>
                <div className="flex flex-wrap items-center gap-2 text-slate-800">
                  <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200 font-bold">
                    Subject(Actor)
                  </span>
                  <span className="text-slate-400">→ [Edge: Owns] →</span>
                  <span className="px-2 py-0.5 rounded bg-sky-50 text-sky-700 border border-sky-200 font-bold">
                    Resource(ID)
                  </span>
                  <span className="text-slate-400">∩</span>
                  <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 border border-amber-200 font-bold">
                    Operation(TenantBoundary)
                  </span>
                </div>
                <div className="text-emerald-700 font-semibold pt-1">
                  ✓ Verdict: If Edge == NULL, block immediately. No heuristics, no LLM hallucinations.
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-200/80 flex items-center justify-between text-xs text-slate-500 font-mono">
              <span>Arbitration Time: &lt;0.3ms</span>
              <span className="text-blue-600 font-semibold">Zero False Drops</span>
            </div>
          </div>

          {/* Card 2: Sub-millisecond Inline Proxy (<1.2ms) (Span 1) */}
          <div className="p-7 rounded-2xl bg-white border border-slate-200 hover:border-slate-300 transition-all flex flex-col justify-between shadow-xs">
            <div>
              <div className="w-10 h-10 rounded-xl bg-sky-50 border border-sky-200 text-sky-700 flex items-center justify-center mb-4">
                <Zap className="w-5 h-5" strokeWidth={2.2} />
              </div>

              <div className="text-xs font-mono font-bold text-sky-700 uppercase tracking-wider mb-1">
                Wire Speed
              </div>
              <h3 className="text-xl font-bold text-slate-900 tracking-tight">
                &lt;1.2ms Latency Overhead
              </h3>
              <p className="text-slate-600 text-sm mt-2 leading-relaxed">
                Compiled into native Envoy Rust filters. Zero stream-buffering, asynchronous telemetry pipelines, and non-blocking zero-copy body inspection.
              </p>

              {/* Latency Comparison Bar */}
              <div className="mt-6 space-y-2 font-mono text-xs">
                <div>
                  <div className="flex justify-between text-slate-600 mb-1">
                    <span>Perimeter Envoy Filter</span>
                    <span className="font-bold text-blue-600">0.9ms</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                    <div className="h-full bg-blue-600 rounded-full w-[12%]" />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-slate-400 mb-1">
                    <span>Legacy WAF Cloud Proxy</span>
                    <span>18.4ms</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
                    <div className="h-full bg-slate-400 rounded-full w-[85%]" />
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 text-xs text-slate-500 font-mono">
              Direct Ingress Gateway Integration
            </div>
          </div>

          {/* Card 3: Dynamic OpenAPI Spec & Drift (Span 1) */}
          <div className="p-7 rounded-2xl bg-white border border-slate-200 hover:border-slate-300 transition-all flex flex-col justify-between shadow-xs">
            <div>
              <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-200 text-amber-700 flex items-center justify-center mb-4">
                <FileCode2 className="w-5 h-5" strokeWidth={2.2} />
              </div>

              <div className="text-xs font-mono font-bold text-amber-700 uppercase tracking-wider mb-1">
                Spec Automation
              </div>
              <h3 className="text-xl font-bold text-slate-900 tracking-tight">
                Dynamic OpenAPI Generation
              </h3>
              <p className="text-slate-600 text-sm mt-2 leading-relaxed">
                Perimeter observes wire payloads to generate validated OpenAPI 3.1 specifications. Instantly flags breaking schema mutations and zombie routes forgotten in legacy deploys.
              </p>

              <div className="mt-5 p-3 rounded-lg bg-slate-50 border border-slate-200 font-mono text-xs space-y-1">
                <div className="text-amber-800 font-semibold">Active Drift Detection</div>
                <div className="text-slate-600 text-[11px] leading-relaxed">
                  Automatically flags when payload parameters diverge from published Git contracts.
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 text-xs text-slate-500 font-mono">
              Supports Swagger 2.0 & OpenAPI 3.1
            </div>
          </div>

          {/* Card 4: Sovereign Compliance & PII Masking (Span 2) */}
          <div className="md:col-span-2 p-7 rounded-2xl bg-[#F8FAFC] border border-slate-200 hover:border-slate-300 transition-all flex flex-col justify-between shadow-xs">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-10 h-10 rounded-xl bg-slate-100 border border-slate-300 text-slate-800 flex items-center justify-center">
                  <Lock className="w-5 h-5" strokeWidth={2.2} />
                </div>
                <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-slate-100 text-slate-800 border border-slate-300">
                  RBI / DPDP / SOC2 READY
                </span>
              </div>

              <h3 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                Automated PII Redaction & Sovereign Compliance
              </h3>
              <p className="text-slate-600 text-sm sm:text-base mt-2 leading-relaxed max-w-xl">
                Inspects request queries, json payloads, and response headers for sensitive personal identifiers (Aadhaar, PAN, UPI IDs, Phone, Credit Cards). Sensitive attributes are masked in flight before entering logging pipelines.
              </p>

              {/* Masking Chips */}
              <div className="mt-6 flex flex-wrap gap-2">
                <span className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs font-mono font-medium text-slate-800 shadow-2xs">
                  PAN: <code className="text-blue-700 font-bold">AAACP****K</code>
                </span>
                <span className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs font-mono font-medium text-slate-800 shadow-2xs">
                  Aadhaar: <code className="text-blue-700 font-bold">XXXX-XXXX-4411</code>
                </span>
                <span className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs font-mono font-medium text-slate-800 shadow-2xs">
                  UPI VPA: <code className="text-blue-700 font-bold">user****@okhdfc</code>
                </span>
                <span className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-xs font-mono font-medium text-slate-800 shadow-2xs">
                  Auth Token: <code className="text-blue-700 font-bold">tok_***[REDACTED]</code>
                </span>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-200/80 flex items-center justify-between text-xs text-slate-500 font-mono">
              <span>Data Sovereignty: On-Premise & Local Cloud</span>
              <span className="text-emerald-700 font-semibold flex items-center gap-1">
                <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                <span>Zero Data Egress to External LLMs</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
