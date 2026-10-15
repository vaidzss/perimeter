import React from 'react';
import { mapDefenseToFlowDiagram } from './mappers';
import { ShieldCheck, Ban, Zap, ArrowRight, Server, Lock, Cpu, Network } from 'lucide-react';

interface RequestPathFlowProps {
  defense?: any;
}

export const RequestPathFlow: React.FC<RequestPathFlowProps> = ({ defense }) => {
  const model = mapDefenseToFlowDiagram(defense);

  return (
    <div className="relative border border-slate-200 rounded-2xl bg-white p-5 select-none shadow-xs">
      {/* Header telemetry */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-100 mb-4 gap-2">
        <div>
          <h3 className="text-[14px] font-semibold text-slate-900 tracking-tight">
            Inline API Defense Topology & Flow Arbitration
          </h3>
          <p className="text-[12px] text-slate-500 mt-0.5">
            Real-time inline proxy inspection, virtual patching, and PII masking
          </p>
        </div>
        <div className="flex items-center gap-2 text-[11.5px] font-medium">
          <span className="px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 font-mono text-[11px]">
            Nominal: {model.nominalTotal.toLocaleString()} req/min
          </span>
          <span className="px-2.5 py-1 rounded-full bg-rose-50 text-rose-800 border border-rose-200 font-mono text-[11px]">
            Dropped: {model.blockedTotal} Exploits
          </span>
        </div>
      </div>

      {/* Connected Architecture Cards Flow */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 relative my-2">
        {/* Stage 1: Ingress */}
        <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 relative flex flex-col justify-between hover:border-slate-300 transition-all">
          <div>
            <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest mb-1.5 flex items-center justify-between">
              <span>Stage 01 · Wire</span>
              <Network className="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div className="font-semibold text-slate-900 text-[13px]">Client Ingress</div>
            <div className="text-[11.5px] text-slate-500 mt-1">Web, Mobile & Partner APIs</div>
          </div>
          <div className="mt-3.5 pt-2 border-t border-slate-200 text-[11px] font-mono text-slate-500">
            TLS Termination
          </div>
        </div>

        {/* Stage 2: Inline Gateway */}
        <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/50 relative flex flex-col justify-between hover:border-blue-300 transition-all shadow-2xs">
          <div>
            <div className="text-[10px] font-mono font-bold text-blue-700 uppercase tracking-widest mb-1.5 flex items-center justify-between">
              <span>Stage 02 · Proxy</span>
              <Zap className="w-3.5 h-3.5 text-blue-600" />
            </div>
            <div className="font-semibold text-slate-900 text-[13px]">Perimeter Gateway</div>
            <div className="text-[11.5px] text-blue-900/80 mt-1">Port 8000 (Inline Envoy)</div>
          </div>
          <div className="mt-3.5 pt-2 border-t border-blue-200 text-[11px] font-mono text-blue-700 font-semibold">
            0.0% False Positives
          </div>
        </div>

        {/* Stage 3: Inspection Filter */}
        <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 relative flex flex-col justify-between hover:border-slate-300 transition-all">
          <div>
            <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest mb-1.5 flex items-center justify-between">
              <span>Stage 03 · Filter</span>
              <Cpu className="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div className="font-semibold text-slate-900 text-[13px]">Identity Graph & Patch</div>
            <div className="text-[11.5px] text-slate-500 mt-1">BOLA & Shadow Route Filter</div>
          </div>
          <div className="mt-3.5 pt-2 border-t border-slate-200 text-[11px] font-mono text-slate-600 font-medium">
            &lt;1.2ms Verification
          </div>
        </div>

        {/* Stage 4: Upstream Core */}
        <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 relative flex flex-col justify-between hover:border-slate-300 transition-all">
          <div>
            <div className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-widest mb-1.5 flex items-center justify-between">
              <span>Stage 04 · Core</span>
              <Server className="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div className="font-semibold text-slate-900 text-[13px]">BharatPay Core</div>
            <div className="text-[11.5px] text-slate-500 mt-1">Port 8001 (Upstream Mesh)</div>
          </div>
          <div className="mt-3.5 pt-2 border-t border-slate-200 text-[11px] font-mono text-emerald-700 font-semibold">
            100% Sanitized Ingress
          </div>
        </div>
      </div>
    </div>
  );
};
