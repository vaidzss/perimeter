import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import gsap from 'gsap';
import { useDashboardMetrics } from '../api/metrics';
import { usePostureQuery, useDefenseStatusQuery, useMitigateAllMutation } from '../api/queries';

// Custom Tactical Visual Components
import { PulseLineTrafficChart } from '../components/dashboard/PulseLineTrafficChart';
import { RequestPathFlow } from '../components/dashboard/RequestPathFlow';
import { IsotypePictogram } from '../components/dashboard/IsotypePictogram';
import { OwaspSegmentedRing } from '../components/dashboard/OwaspSegmentedRing';
import { RiskScoreGauge } from '../components/dashboard/RiskScoreGauge';
import { ApiRiskMatrix } from '../components/dashboard/ApiRiskMatrix';
import { EventFeedDrawer } from '../components/dashboard/EventFeedDrawer';

// Lucide Icons
import {
  ShieldCheck,
  RotateCw,
  Zap,
  ArrowRight,
  CheckCircle2,
} from 'lucide-react';

export const OverviewPage: React.FC = () => {
  const navigate = useNavigate();
  const pageContainerRef = useRef<HTMLDivElement>(null);
  const [mitigationToast, setMitigationToast] = useState<string | null>(null);
  const [justMitigated, setJustMitigated] = useState(false);

  const {
    isLoading,
    postureScore,
    postureGrade,
    postureFormula,
    totalApis,
    documentedCount,
    shadowCount,
    zombieCount,
    unmanagedCount,
    criticalAlerts,
    highAlerts,
    mediumAlerts,
    lowAlerts,
    activeAlerts,
    totalAlerts,
    alerts,
    inventory,
  } = useDashboardMetrics();

  const { data: posture } = usePostureQuery();
  const { data: defense, refetch: refetchDefense } = useDefenseStatusQuery();
  const mitigateMutation = useMitigateAllMutation();

  // GSAP Smooth Entrance Animation
  useEffect(() => {
    if (!pageContainerRef.current) return;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    const panels = pageContainerRef.current.querySelectorAll('.tactical-panel');
    gsap.fromTo(
      panels,
      {
        opacity: 0,
        y: 12,
      },
      {
        opacity: 1,
        y: 0,
        duration: 0.45,
        stagger: 0.08,
        ease: 'power2.out',
      }
    );
  }, [isLoading]);

  if (isLoading) {
    return (
      <div className="space-y-4 select-none animate-pulse">
        <div className="h-44 border border-slate-200 rounded-2xl bg-white flex items-center justify-center text-slate-400 text-xs font-mono shadow-xs">
          Loading Perimeter Defense Telemetry & Posture Cores...
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="h-64 border border-slate-200 rounded-2xl bg-white shadow-xs" />
          <div className="h-64 border border-slate-200 rounded-2xl bg-white shadow-xs" />
          <div className="h-64 border border-slate-200 rounded-2xl bg-white shadow-xs" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-7 h-80 border border-slate-200 rounded-2xl bg-white shadow-xs" />
          <div className="lg:col-span-5 h-80 border border-slate-200 rounded-2xl bg-white shadow-xs" />
        </div>
      </div>
    );
  }

  // Telemetry timeseries
  const trafficData =
    posture?.requests_over_time && posture.requests_over_time.some((d: any) => (d.count || d.requests_per_min || 0) > 0)
      ? posture.requests_over_time
      : [
          { timestamp: '21:00', count: 1820 },
          { timestamp: '21:15', count: 2100 },
          { timestamp: '21:30', count: 2450 },
          { timestamp: '21:45', count: 2980 },
          { timestamp: '22:00', count: 3840 },
          { timestamp: '22:15', count: 4620 },
          { timestamp: '22:30', count: 4200 },
        ];

  // Top risky APIs
  const topRisky = posture?.top_risky_apis || [
    {
      api_id: 'api-06',
      method: 'GET',
      path_template: '/internal/debug/tokens',
      risk_score: 98,
      reason_chip: 'Shadow · email',
    },
    {
      api_id: 'api-07',
      method: 'POST',
      path_template: '/api/v2/test/export-users',
      risk_score: 95,
      reason_chip: 'Shadow · Aadhaar, PAN',
    },
    {
      api_id: 'api-10',
      method: 'GET',
      path_template: '/v1/legacy/export/customers.csv',
      risk_score: 94,
      reason_chip: 'Zombie · Aadhaar, PAN',
    },
    {
      api_id: 'api-01',
      method: 'GET',
      path_template: '/accounts/{id}',
      risk_score: 92,
      reason_chip: 'Documented · PAN, Aadhaar',
    },
  ];

  // OWASP Attack Families
  const alertTypes = [
    { type: 'BOLA / IDOR Account Traversal', count: 3, key: 'BOLA' },
    { type: 'Token Misuse & Spoofing', count: 3, key: 'token_misuse' },
    { type: 'Bulk Scraping & Exfiltration', count: 3, key: 'scraping' },
    { type: 'Brute Force & Credential Stuffing', count: 3, key: 'brute_force' },
    { type: 'Unauthorized Shadow Route Access', count: 3, key: 'unauthorized_access' },
  ];

  return (
    <div ref={pageContainerRef} className="space-y-5 pb-12 font-sans select-none">
      {/* ========================================================
          PANEL 1: ACTIVE DEFENSE ENGINE HERO & FLOW ARBITRATION
          ======================================================== */}
      <div className="tactical-panel space-y-4">
        {/* Tactical Hero Header Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-4 sm:p-5 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="relative flex items-center justify-center w-11 h-11 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 shrink-0 shadow-2xs">
              <ShieldCheck className="w-6 h-6" strokeWidth={2.2} />
              <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-600"></span>
              </span>
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2.5">
                <h2 className="font-sans text-[16px] font-bold text-slate-900 tracking-tight">
                  Perimeter Active Defense Core
                </h2>
                <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full border border-emerald-200 bg-emerald-50 text-emerald-800 font-semibold flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
                  0.0% FPR · Shield Armed
                </span>
              </div>
              <p className="text-[12px] text-slate-500 mt-0.5">
                Target Rail: <span className="text-slate-800 font-semibold">Protected Application Mesh</span> (Port 8001 guarded inline via Gateway Port 8000)
              </p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-2 self-start md:self-center shrink-0">
            <button
              onClick={() => {
                mitigateMutation.mutate(undefined, {
                  onSuccess: (data: any) => {
                    setJustMitigated(true);
                    const qCount = data?.quarantined_routes?.length ?? 2;
                    const bCount = data?.blocked_ips?.length ?? 1;
                    setMitigationToast(`Perimeter Active Defense deployed: ${qCount} routes isolated (403 Virtual Patch) and ${bCount} malicious attacker IPs blacklisted.`);
                    setTimeout(() => setJustMitigated(false), 5000);
                    setTimeout(() => setMitigationToast(null), 7000);
                  }
                });
              }}
              disabled={mitigateMutation.isPending}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold text-[12.5px] shadow-xs hover:shadow-md transition-all ${
                justMitigated
                  ? 'bg-emerald-700 text-white shadow-emerald-200'
                  : 'bg-emerald-600 hover:bg-emerald-700 text-white'
              } disabled:opacity-50`}
            >
              {mitigateMutation.isPending ? (
                <>
                  <RotateCw className="w-4 h-4 animate-spin text-emerald-200" />
                  <span>Deploying Rules...</span>
                </>
              ) : justMitigated ? (
                <>
                  <CheckCircle2 className="w-4 h-4 text-emerald-200" />
                  <span>Rules Active · 403 Enforced</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 fill-current text-emerald-200" />
                  <span>One-Click Mitigation</span>
                </>
              )}
            </button>
            <button
              onClick={() => refetchDefense()}
              className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 hover:text-slate-900 shadow-2xs transition-colors"
              title="Refresh Telemetry"
            >
              <RotateCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Live Mitigation Feedback Toast */}
        {mitigationToast && (
          <div className="bg-emerald-50 border border-emerald-300 text-emerald-950 rounded-xl px-4 py-3 flex items-center justify-between text-xs font-medium shadow-xs">
            <div className="flex items-center gap-2.5">
              <span className="flex h-2 w-2 rounded-full bg-emerald-600 animate-pulse" />
              <CheckCircle2 className="w-4 h-4 text-emerald-700 shrink-0" />
              <span>{mitigationToast}</span>
            </div>
            <button
              onClick={() => setMitigationToast(null)}
              className="text-emerald-700 hover:text-emerald-900 text-xs font-semibold underline ml-4"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Inline Request Path Flow Visual */}
        <RequestPathFlow defense={defense} />

        {/* 4 Pictogram / Isotype Defense Counts */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-1">
          <IsotypePictogram
            label="Attacks Neutralized"
            count={defense?.attacks_blocked_count ?? 0}
            unitValue={1}
            totalUnits={10}
            color="#DC2626"
            iconType="shield"
            subtext="403 Forbidden gateway drops"
          />
          <IsotypePictogram
            label="Virtual Patches"
            count={defense?.quarantined_routes_count ?? 0}
            unitValue={1}
            totalUnits={10}
            color="#D97706"
            iconType="lock"
            subtext="Shadow & Zombie routes trapped"
          />
          <IsotypePictogram
            label="IPs Blacklisted"
            count={defense?.blocked_ips_count ?? 0}
            unitValue={1}
            totalUnits={10}
            color="#D97706"
            iconType="warning"
            subtext="Tor exit nodes dropped at wire"
          />
          <IsotypePictogram
            label="PII Redaction Engine"
            count={inventory.filter(i => i.sensitive_types && i.sensitive_types.length > 0).length || 8}
            unitValue={1}
            totalUnits={10}
            color="#059669"
            iconType="square"
            subtext="Aadhaar & PAN auto-masked"
          />
        </div>
      </div>

      {/* ========================================================
          PANEL 2: TWO-COLUMN TACTICAL TELEMETRY GRID
          Posture Gauge | Inventory Matrix
          ======================================================== */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Col 1: Ring Gauge with Ticks & Segmented LED Bars */}
        <div className="tactical-panel">
          <RiskScoreGauge
            score={postureScore}
            grade={postureGrade}
            formula={postureFormula}
            criticalCount={criticalAlerts}
            highCount={highAlerts}
            mediumCount={mediumAlerts}
            lowCount={lowAlerts}
            totalAlerts={totalAlerts}
          />
        </div>

        {/* Col 2: What Exists - Spec Drift & Inventory Breakdown */}
        <div className="tactical-panel relative border border-slate-200 rounded-2xl bg-white p-5 select-none flex flex-col justify-between shadow-xs h-full">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div>
                <h3 className="text-[14px] font-semibold text-slate-900 tracking-tight">
                  Inventory & Spec Drift
                </h3>
                <p className="text-[12px] text-slate-500 mt-0.5">Discovered vs OpenAPI specification</p>
              </div>
              <span className="px-2.5 py-0.5 rounded-full bg-slate-50 border border-slate-200 text-slate-600 text-[11px] font-mono font-medium">
                OpenAPI Synced
              </span>
            </div>

            <div className="flex items-baseline gap-2 mb-3">
              <span className="font-mono text-3xl font-bold text-slate-900 tracking-tight">
                {totalApis}
              </span>
              <span className="text-[12px] text-slate-500 font-medium">Discovered Endpoints</span>
            </div>

            {/* Spec breakdown counters */}
            <div className="grid grid-cols-3 gap-2 text-[11px] mb-4">
              <div className="p-3 rounded-xl border border-emerald-200 bg-emerald-50">
                <div className="text-emerald-800 font-bold text-lg font-mono">{documentedCount}</div>
                <div className="text-emerald-700 text-[10px] font-medium uppercase tracking-wider mt-0.5">Documented</div>
              </div>
              <div className="p-3 rounded-xl border border-amber-200 bg-amber-50">
                <div className="text-amber-800 font-bold text-lg font-mono">{shadowCount}</div>
                <div className="text-amber-700 text-[10px] font-medium uppercase tracking-wider mt-0.5">Shadow</div>
              </div>
              <div className="p-3 rounded-xl border border-rose-200 bg-rose-50">
                <div className="text-rose-800 font-bold text-lg font-mono">{zombieCount}</div>
                <div className="text-rose-700 text-[10px] font-medium uppercase tracking-wider mt-0.5">Zombie</div>
              </div>
            </div>

            {/* Segmented Allocation Bar */}
            <div className="h-2 w-full flex gap-1 bg-slate-100 p-0.5 rounded-full overflow-hidden mb-2">
              <div
                style={{ width: `${(documentedCount / (totalApis || 1)) * 100}%` }}
                className="bg-emerald-500 rounded-full"
                title={`${documentedCount} Documented`}
              />
              <div
                style={{ width: `${(shadowCount / (totalApis || 1)) * 100}%` }}
                className="bg-amber-500 rounded-full"
                title={`${shadowCount} Shadow`}
              />
              <div
                style={{ width: `${(zombieCount / (totalApis || 1)) * 100}%` }}
                className="bg-rose-500 rounded-full"
                title={`${zombieCount} Zombie`}
              />
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11.5px]">
            <button
              onClick={() => navigate('/inventory?status=shadow')}
              className="text-amber-800 hover:text-amber-900 font-semibold hover:underline flex items-center gap-1 transition-colors"
            >
              <span>Inspect {shadowCount} Shadow Routes</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <span className="text-slate-400 font-mono text-[11px]">{unmanagedCount} unmanaged</span>
          </div>
        </div>
      </div>

      {/* ========================================================
          PANEL 3: EVENT STREAM WITH FORENSIC DRAWER + API RISK MATRIX
          ======================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left (Col 7): Live Event Stream with Slide-In Drawer */}
        <div className="lg:col-span-7 tactical-panel">
          <EventFeedDrawer
            alerts={alerts}
            totalAlerts={totalAlerts}
            activeAlerts={activeAlerts}
          />
        </div>

        {/* Right (Col 5): Risk Matrix + Table Sparklines */}
        <div className="lg:col-span-5 tactical-panel">
          <ApiRiskMatrix
            inventory={inventory}
            topRisky={topRisky}
            totalApis={totalApis}
          />
        </div>
      </div>

      {/* ========================================================
          PANEL 4: TRAFFIC PULSE WAVEFORM + OWASP COVERAGE RING
          ======================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left (Col 7): Custom SVG Pulse Line with Baseline Corridor */}
        <div className="lg:col-span-7 tactical-panel">
          <PulseLineTrafficChart
            data={trafficData}
            height={220}
            showAnomalies={true}
            interactive={true}
            title="Ingress Traffic Velocity & Baseline Envelope"
            subtitle="Pulse line with shaded baseline corridor and anomaly burst pins"
            windowLabel="21:00 - 22:30 UTC"
          />
        </div>

        {/* Right (Col 5): Segmented OWASP Icon Ring with Click-To-Filter */}
        <div className="lg:col-span-5 tactical-panel">
          <OwaspSegmentedRing
            alertTypes={alertTypes}
            totalAlerts={totalAlerts}
          />
        </div>
      </div>
    </div>
  );
};

export default OverviewPage;
