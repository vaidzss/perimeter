import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import gsap from 'gsap';
import { Alert } from '../../types';
import { MethodTag } from '../common/MethodTag';
import { SeverityDot } from '../common/SeverityDot';
import { RelativeTime } from '../common/RelativeTime';
import { X, ArrowRight, ShieldCheck, Terminal, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface EventFeedDrawerProps {
  alerts: Alert[];
  totalAlerts?: number;
  activeAlerts?: number;
}

export const EventFeedDrawer: React.FC<EventFeedDrawerProps> = ({
  alerts,
  totalAlerts = 15,
  activeAlerts = 9,
}) => {
  const navigate = useNavigate();
  const [selectedIdx, setSelectedIdx] = useState(0);
  const [drawerAlert, setDrawerAlert] = useState<Alert | null>(null);
  const drawerRef = useRef<HTMLDivElement>(null);

  const displayAlerts = alerts.slice(0, 8);

  // Keyboard navigation: j/k to move, Enter to inspect
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (document.activeElement?.tagName === 'INPUT') return;
      if (e.key === 'j') {
        setSelectedIdx((prev) => Math.min(prev + 1, displayAlerts.length - 1));
      } else if (e.key === 'k') {
        setSelectedIdx((prev) => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter') {
        if (displayAlerts[selectedIdx]) {
          setDrawerAlert(displayAlerts[selectedIdx]);
        }
      } else if (e.key === 'Escape') {
        setDrawerAlert(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [displayAlerts, selectedIdx]);

  // GSAP animation for forensic drawer slide-in
  useEffect(() => {
    if (!drawerRef.current) return;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    if (drawerAlert) {
      gsap.fromTo(
        drawerRef.current,
        { x: '100%', opacity: 0 },
        { x: '0%', opacity: 1, duration: 0.3, ease: 'power3.out' }
      );
    }
  }, [drawerAlert]);

  return (
    <div className="relative border border-slate-200 rounded-2xl bg-white p-5 select-none flex flex-col justify-between shadow-xs h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <div>
            <h3 className="text-[14px] font-semibold text-slate-900 tracking-tight">
              Real-Time Security Enforcement Feed
            </h3>
            <p className="text-[12px] text-slate-500 mt-0.5">
              Live virtual patch enforcement stream (j/k to navigate, Enter to inspect)
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 text-[11px] font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
              <span>{activeAlerts} Active Drops</span>
            </span>
          </div>
        </div>

        {/* Live List Items */}
        <div className="space-y-1.5 max-h-[360px] overflow-y-auto pr-1">
          {displayAlerts.map((alert, idx) => {
            const isSelected = idx === selectedIdx;
            return (
              <div
                key={alert.alert_id}
                onClick={() => setDrawerAlert(alert)}
                onMouseEnter={() => setSelectedIdx(idx)}
                className={`p-3 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-blue-50/70 border-blue-200 shadow-2xs'
                    : 'bg-white hover:bg-slate-50 border-slate-100'
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1">
                  <div className="flex items-center gap-2 truncate">
                    <SeverityDot severity={alert.severity} showLabel={false} />
                    <span className="font-semibold text-xs text-slate-900 truncate">
                      {alert.type}
                    </span>
                  </div>
                  <span className="text-[10.5px] font-mono text-slate-400 shrink-0">
                    <RelativeTime timestamp={alert.last_seen} />
                  </span>
                </div>

                <div className="flex items-center justify-between text-[11px] text-slate-600 font-mono mt-1">
                  <span className="truncate max-w-[240px] text-slate-700">{alert.api}</span>
                  <span className="text-slate-400 shrink-0">Actor: {alert.actor}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer Info */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-mono">
        <span>Keyboard: j / k / Enter</span>
        <button
          onClick={() => navigate('/alerts')}
          className="hover:text-blue-600 font-semibold flex items-center gap-1 transition-colors"
        >
          <span>All {totalAlerts} Alerts</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Slide-out Forensic Drawer */}
      {drawerAlert && (
        <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-xs">
          <div
            ref={drawerRef}
            className="w-full max-w-lg h-full bg-white border-l border-slate-200 shadow-2xl flex flex-col text-slate-900"
          >
            {/* Header */}
            <div className="p-5 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <SeverityDot severity={drawerAlert.severity} />
                  <span className="font-mono text-xs font-semibold text-slate-500">
                    {drawerAlert.alert_id}
                  </span>
                </div>
                <h3 className="text-base font-bold text-slate-900">{drawerAlert.type}</h3>
              </div>
              <button
                onClick={() => setDrawerAlert(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content Body */}
            <div className="flex-1 overflow-y-auto p-5 space-y-5">
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 space-y-2 text-xs">
                <div>
                  <span className="text-[10.5px] font-mono text-slate-400 uppercase">Target Endpoint</span>
                  <div className="font-mono font-bold text-slate-900 mt-0.5">{drawerAlert.api}</div>
                </div>
                <div>
                  <span className="text-[10.5px] font-mono text-slate-400 uppercase">Threat Classification</span>
                  <div className="font-mono text-slate-800 mt-0.5">{drawerAlert.owasp}</div>
                </div>
                <div>
                  <span className="text-[10.5px] font-mono text-slate-400 uppercase">Authenticated Actor</span>
                  <div className="font-mono text-blue-600 font-semibold mt-0.5">{drawerAlert.actor}</div>
                </div>
                <div>
                  <span className="text-[10.5px] font-mono text-slate-400 uppercase">Detection Rationale</span>
                  <div className="text-slate-700 mt-0.5 leading-relaxed">{drawerAlert.reason}</div>
                </div>
              </div>

              {/* Ingress Wire Payload Forensic Box */}
              <div>
                <div className="text-xs font-semibold text-slate-700 mb-2">Wire Request Payload</div>
                <div className="p-4 rounded-xl bg-slate-900 text-slate-100 font-mono text-xs overflow-x-auto shadow-inner">
                  <pre className="text-emerald-400 leading-tight">
                    {JSON.stringify(
                      {
                        method: 'GET',
                        uri: drawerAlert.api,
                        actor_id: drawerAlert.actor,
                        threat_family: drawerAlert.owasp,
                        verdict: '403_FORBIDDEN_PATCH',
                      },
                      null,
                      2
                    )}
                  </pre>
                </div>
              </div>

              {/* Virtual Patch Action Box */}
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-start gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <div className="text-xs font-bold text-emerald-900">Virtual Patch Applied</div>
                  <div className="text-xs text-emerald-800 mt-0.5 leading-relaxed">
                    Perimeter Envoy filter dropped caller connection inline within &lt;1.1ms. Zero malicious traffic reached upstream backend containers.
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
              <Link
                to={`/alerts/${drawerAlert.alert_id}`}
                className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-2xs"
              >
                <span>Open Deep Forensics</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
              <button
                onClick={() => setDrawerAlert(null)}
                className="px-3 py-2 text-xs font-medium text-slate-600 hover:text-slate-900"
              >
                Close (Esc)
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
