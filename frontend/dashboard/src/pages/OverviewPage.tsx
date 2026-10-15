import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDashboardMetrics } from '../api/metrics';
import { usePostureQuery, useDefenseStatusQuery, useMitigateAllMutation } from '../api/queries';
import { SeverityDot } from '../components/common/SeverityDot';
import { MethodTag } from '../components/common/MethodTag';
import { RelativeTime } from '../components/common/RelativeTime';
import {
  ArrowRight,
  ChevronRight,
  ShieldCheck,
  ShieldAlert,
  Lock,
  CheckCircle2,
  Ban,
  Zap,
  RefreshCw
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceArea,
  ReferenceLine,
  CartesianGrid
} from 'recharts';

export const OverviewPage: React.FC = () => {
  const navigate = useNavigate();
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
    unusedCount,
    criticalAlerts,
    highAlerts,
    mediumAlerts,
    lowAlerts,
    activeAlerts,
    alerts,
  } = useDashboardMetrics();

  const { data: posture } = usePostureQuery();
  const { data: defense, refetch: refetchDefense } = useDefenseStatusQuery();
  const mitigateMutation = useMitigateAllMutation();
  const [selectedAlertIdx, setSelectedAlertIdx] = useState<number>(0);

  // Keyboard navigation for table (j/k to move, Enter to navigate)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if focus is in an input
      if (document.activeElement?.tagName === 'INPUT') return;

      const activeAlertList = alerts.slice(0, 8);
      if (e.key === 'j') {
        setSelectedAlertIdx(prev => Math.min(prev + 1, activeAlertList.length - 1));
      } else if (e.key === 'k') {
        setSelectedAlertIdx(prev => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter') {
        if (activeAlertList[selectedAlertIdx]) {
          navigate(`/alerts/${activeAlertList[selectedAlertIdx].alert_id}`);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [alerts, selectedAlertIdx, navigate]);

  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        {/* Row 1 skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="h-40 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
          <div className="h-40 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
          <div className="h-40 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
        </div>
        {/* Row 2 skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-8 h-80 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
          <div className="lg:col-span-4 h-80 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
        </div>
      </div>
    );
  }

  // Row 1: What exists stacked bar calculations
  const totalBarCount = totalApis || 20;
  const docPct = ((documentedCount / totalBarCount) * 100).toFixed(1);
  const shadowPct = ((shadowCount / totalBarCount) * 100).toFixed(1);
  const zombiePct = ((zombieCount / totalBarCount) * 100).toFixed(1);
  const unmanagedPct = ((unmanagedCount / totalBarCount) * 100).toFixed(1);
  const unusedPct = ((unusedCount / totalBarCount) * 100).toFixed(1);

  // Row 1: Traffic mini data
  const miniTraffic = (posture?.requests_over_time || [
    { timestamp: '21:00', count: 1820 },
    { timestamp: '21:15', count: 2100 },
    { timestamp: '21:30', count: 2450 },
    { timestamp: '21:45', count: 2980 },
    { timestamp: '22:00', count: 3840 },
    { timestamp: '22:15', count: 4620 },
    { timestamp: '22:30', count: 4200 },
  ]);

  // Row 1: What's risky stacked severity bar
  const totalSeverities = (criticalAlerts + highAlerts + mediumAlerts + lowAlerts) || 15;
  const critPct = (criticalAlerts / totalSeverities) * 100;
  const highPct = (highAlerts / totalSeverities) * 100;
  const medPct = (mediumAlerts / totalSeverities) * 100;
  const lowPct = (lowAlerts / totalSeverities) * 100;

  // Row 2: Active "Needs attention" alerts
  const queueAlerts = alerts.slice(0, 8);

  // Row 2: Top 5 risky APIs
  const topRisky = posture?.top_risky_apis || [
    { api_id: 'api-06', method: 'GET', path_template: '/internal/debug/tokens', risk_score: 98, reason_chip: 'Shadow · email' },
    { api_id: 'api-07', method: 'POST', path_template: '/api/v2/test/export-users', risk_score: 95, reason_chip: 'Shadow · Aadhaar, PAN' },
    { api_id: 'api-10', method: 'GET', path_template: '/v1/legacy/export/customers.csv', risk_score: 94, reason_chip: 'Zombie · Aadhaar, PAN' },
    { api_id: 'api-01', method: 'GET', path_template: '/accounts/{id}', risk_score: 92, reason_chip: 'Documented · PAN, Aadhaar' },
    { api_id: 'api-13', method: 'GET', path_template: '/cards/{id}/statement', risk_score: 89, reason_chip: 'Documented · PAN, email' },
  ];

  // Row 3: Alerts by type breakdown
  const alertTypes = [
    { type: 'BOLA / IDOR', count: 3, key: 'BOLA' },
    { type: 'Token misuse', count: 3, key: 'token_misuse' },
    { type: 'Bulk scraping', count: 3, key: 'scraping' },
    { type: 'Brute force', count: 3, key: 'brute_force' },
    { type: 'Unauthorized', count: 3, key: 'unauthorized_access' },
  ];

  return (
    <div className="space-y-4">
      {/* ========================================================
          HERO ACTIVE DEFENSE STATUS & LIVE ATTACK SHIELD
          ======================================================== */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 space-y-4">
        {/* Header with live shield pulse */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-[#252A31]">
          <div className="flex items-center gap-3">
            <div className="relative flex items-center justify-center w-8 h-8 rounded-full bg-[#10b981]/10 border border-[#10b981]/30">
              <ShieldCheck className="w-4 h-4 text-[#10b981]" strokeWidth={2} />
              <span className="absolute -top-0.5 -right-0.5 flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#10b981] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#10b981]"></span>
              </span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-[14px] font-semibold text-[#E6E8EB]">Perimeter Active Defense</h2>
                <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 rounded-[3px] bg-[#10b981]/15 text-[#10b981] border border-[#10b981]/30 font-medium">
                  Shield Engaged
                </span>
              </div>
              <p className="text-[11px] text-[#8B929C]">
                Target System: <span className="text-[#E6E8EB] font-mono">BharatPay Core Banking</span> (Port 8001 proxied & guarded via Port 8000)
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => mitigateMutation.mutate()}
              disabled={mitigateMutation.isPending}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-[4px] bg-[#4C8DFF] hover:bg-[#3B7BF6] text-white text-[11px] font-medium transition-colors shadow-xs disabled:opacity-50"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>{mitigateMutation.isPending ? 'Deploying Patches...' : 'Deploy One-Click Mitigation'}</span>
            </button>
            <button
              onClick={() => refetchDefense()}
              className="p-1.5 rounded-[4px] bg-[#0E1013] border border-[#252A31] hover:border-[#343B45] text-[#8B929C] hover:text-[#E6E8EB] transition-colors"
              title="Refresh Defense Status"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* 4 Defense KPI Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-[#0E1013] border border-[#252A31] rounded-[4px] p-3">
            <div className="flex items-center justify-between text-[11px] text-[#8B929C] mb-1">
              <span>Attacks Blocked</span>
              <Ban className="w-3.5 h-3.5 text-[#E5484D]" />
            </div>
            <div className="text-[18px] font-semibold text-[#E5484D] font-mono">
              {defense?.attacks_blocked_count || 4}
            </div>
            <div className="text-[10px] text-[#8B929C]">HTTP 403 Forbidden drops</div>
          </div>

          <div className="bg-[#0E1013] border border-[#252A31] rounded-[4px] p-3">
            <div className="flex items-center justify-between text-[11px] text-[#8B929C] mb-1">
              <span>Virtual Patches</span>
              <Lock className="w-3.5 h-3.5 text-[#B47AEA]" />
            </div>
            <div className="text-[18px] font-semibold text-[#B47AEA] font-mono">
              {defense?.quarantined_routes_count || 2} Routes
            </div>
            <div className="text-[10px] text-[#8B929C]">Zombie & Shadow quarantined</div>
          </div>

          <div className="bg-[#0E1013] border border-[#252A31] rounded-[4px] p-3">
            <div className="flex items-center justify-between text-[11px] text-[#8B929C] mb-1">
              <span>IPs Blacklisted</span>
              <ShieldAlert className="w-3.5 h-3.5 text-[#F76B15]" />
            </div>
            <div className="text-[18px] font-semibold text-[#F76B15] font-mono">
              {defense?.blocked_ips_count || 1} Host
            </div>
            <div className="text-[10px] text-[#8B929C]">Tor exit nodes dropped at edge</div>
          </div>

          <div className="bg-[#0E1013] border border-[#252A31] rounded-[4px] p-3">
            <div className="flex items-center justify-between text-[11px] text-[#8B929C] mb-1">
              <span>In-Flight PII Redaction</span>
              <CheckCircle2 className="w-3.5 h-3.5 text-[#10b981]" />
            </div>
            <div className="text-[18px] font-semibold text-[#10b981] font-mono">
              ACTIVE
            </div>
            <div className="text-[10px] text-[#8B929C]">Raw Aadhaar & PAN masked</div>
          </div>
        </div>

        {/* Live Attack Resolutions & Enforcement Table (Which API got allowed vs blocked) */}
        <div className="space-y-2 pt-1">
          <div className="flex items-center justify-between text-[12px] font-medium text-[#E6E8EB]">
            <span>Live Attack Resolutions & Policy Enforcements</span>
            <span className="text-[11px] font-mono text-[#8B929C]">
              {defense?.enforcements?.length || 0} policy decisions
            </span>
          </div>

          <div className="overflow-x-auto border border-[#252A31] rounded-[4px]">
            <table className="w-full text-left text-[11px] font-mono">
              <thead className="bg-[#0E1013] text-[#8B929C] border-b border-[#252A31] font-sans">
                <tr className="h-7">
                  <th className="px-3 font-normal">Target Endpoint</th>
                  <th className="px-3 font-normal w-28">Decision</th>
                  <th className="px-3 font-normal">Attack Vector / Threat</th>
                  <th className="px-3 font-normal">Perimeter Protection Result</th>
                  <th className="px-3 font-normal w-28">Source / Actor</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#252A31]">
                {(defense?.enforcements || []).slice(0, 6).map((enf: any, i: number) => {
                  const isBlocked = enf.decision === 'BLOCKED' || enf.decision === 'QUARANTINED' || enf.decision === 'BLACKLISTED';
                  return (
                    <tr key={i} className="h-8 hover:bg-[#1C2026] transition-colors">
                      <td className="px-3 text-[#E6E8EB] whitespace-nowrap">
                        <span className="text-[#4C8DFF] mr-1.5 font-medium">{enf.method}</span>
                        <span>{enf.target}</span>
                      </td>
                      <td className="px-3 whitespace-nowrap">
                        <span className={`px-1.5 py-0.5 rounded-[3px] text-[10px] font-medium border ${
                          isBlocked
                            ? 'bg-[#E5484D]/15 text-[#E5484D] border-[#E5484D]/30'
                            : 'bg-[#10b981]/15 text-[#10b981] border-[#10b981]/30'
                        }`}>
                          {enf.decision} ({enf.http_status})
                        </span>
                      </td>
                      <td className="px-3 text-[#E6E8EB] whitespace-nowrap font-sans text-[11px]">
                        {enf.attack_vector}
                      </td>
                      <td className="px-3 text-[#8B929C] font-sans text-[11px]">
                        {enf.impact}
                      </td>
                      <td className="px-3 text-[#8B929C] whitespace-nowrap">
                        {enf.client_ip}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ========================================================
          ROW 1: THREE QUESTION PANELS (EQUAL WIDTH, NO HERO BANNER)
          ======================================================== */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Panel 1: What exists (Inventory) */}
        <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-[11px] text-[#8B929C] mb-2">
              <span className="font-medium text-[#E6E8EB]">What exists</span>
              <span>Inventory & shadow diff</span>
            </div>

            {/* Metric line */}
            <div className="text-[12px] text-[#8B929C] mb-3">
              <span className="text-[#E6E8EB] font-medium text-[15px]">{totalApis} discovered</span>
              <span className="mx-1.5 text-[#343B45]">·</span>
              <span>{documentedCount} documented</span>
              <span className="mx-1.5 text-[#343B45]">·</span>
              <span className="text-[#B47AEA]">{shadowCount} shadow</span>
              <span className="mx-1.5 text-[#343B45]">·</span>
              <span className="text-[#E5484D]">{zombieCount} zombie</span>
              <span className="mx-1.5 text-[#343B45]">·</span>
              <span className="text-[#F76B15]">{unmanagedCount} unmanaged</span>
            </div>

            {/* Single stacked horizontal bar (clickable segments) */}
            <div className="h-2 w-full rounded-full overflow-hidden flex bg-[#0E1013] gap-0.5 cursor-pointer">
              <Link
                to="/inventory?status=documented"
                title={`${documentedCount} Documented (${docPct}%)`}
                style={{ width: `${docPct}%` }}
                className="bg-[#3A424E] hover:bg-[#4C8DFF] transition-colors"
              />
              <Link
                to="/inventory?status=shadow"
                title={`${shadowCount} Shadow (${shadowPct}%)`}
                style={{ width: `${shadowPct}%` }}
                className="bg-[#B47AEA] hover:opacity-85 transition-opacity"
              />
              <Link
                to="/inventory?status=zombie"
                title={`${zombieCount} Zombie (${zombiePct}%)`}
                style={{ width: `${zombiePct}%` }}
                className="bg-[#E5484D] hover:opacity-85 transition-opacity"
              />
              <Link
                to="/inventory?status=unmanaged"
                title={`${unmanagedCount} Unmanaged (${unmanagedPct}%)`}
                style={{ width: `${unmanagedPct}%` }}
                className="bg-[#F76B15] hover:opacity-85 transition-opacity"
              />
              <Link
                to="/inventory?status=unused_documented"
                title={`${unusedCount} Unused (${unusedPct}%)`}
                style={{ width: `${unusedPct}%` }}
                className="bg-[#5C626C] hover:opacity-85 transition-opacity"
              />
            </div>
          </div>

          <div className="pt-3 mt-3 border-t border-[#252A31] flex items-center justify-between text-[11px]">
            <Link
              to="/inventory?status=shadow"
              className="text-[#B47AEA] hover:underline flex items-center gap-1"
            >
              <span>Inspect {shadowCount} uncataloged shadow endpoints</span>
              <ArrowRight className="w-3 h-3" strokeWidth={1.5} />
            </Link>
            <span className="text-[#8B929C] font-mono text-[10px]">openapi.yaml sync</span>
          </div>
        </div>

        {/* Panel 2: How it's used (Behavior) */}
        <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-[11px] text-[#8B929C] mb-1">
              <span className="font-medium text-[#E6E8EB]">How it's used</span>
              <span>Traffic & baselines</span>
            </div>

            {/* Sparkline line chart with anomaly window shaded */}
            <div className="h-12 w-full my-1">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={miniTraffic} margin={{ top: 2, right: 0, left: 0, bottom: 2 }}>
                  <defs>
                    <linearGradient id="miniTrafficGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#4C8DFF" stopOpacity={0.25} />
                      <stop offset="100%" stopColor="#4C8DFF" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  {/* Shaded anomaly burst window between 22:00 and 22:30 */}
                  <ReferenceArea x1="22:00" x2="22:30" fill="#E5484D" fillOpacity={0.12} stroke="#E5484D" strokeOpacity={0.3} />
                  <Area
                    type="monotone"
                    dataKey="count"
                    stroke="#4C8DFF"
                    strokeWidth={1.5}
                    fill="url(#miniTrafficGrad)"
                    dot={false}
                    isAnimationActive={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="text-[12px] text-[#E6E8EB] flex items-center gap-1.5 mt-1">
              <span className="w-1.5 h-1.5 rounded-full bg-[#E5484D]" />
              <span>2 endpoints deviating from baseline (burst anomaly)</span>
            </div>
          </div>

          <div className="pt-3 mt-3 border-t border-[#252A31] flex items-center justify-between text-[11px]">
            <Link to="/traffic" className="text-[#8B929C] hover:text-[#E6E8EB] flex items-center gap-1 transition-colors">
              <span>View telemetry & latency profiles</span>
              <ArrowRight className="w-3 h-3" strokeWidth={1.5} />
            </Link>
            <span className="text-[#8B929C] font-mono text-[10px]">4,620 peak req/min</span>
          </div>
        </div>

        {/* Panel 3: What's risky (Risk) */}
        <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between text-[11px] text-[#8B929C] mb-2">
              <span className="font-medium text-[#E6E8EB]">What is risky</span>
              <span>Posture score & severity distribution</span>
            </div>

            {/* Score number and grade */}
            <div className="flex items-baseline gap-2 mb-2">
              <span className="text-2xl font-semibold text-[#E6E8EB] font-mono tracking-tight">
                {postureScore}
              </span>
              <span className="text-[12px] text-[#8B929C] font-mono">/ 100</span>
              <span className="text-[11px] text-[#E5A100] font-mono ml-2 border border-[#E5A100]/30 px-1.5 py-0.2 rounded-[3px] bg-[#E5A100]/10">
                {postureGrade}
              </span>
            </div>

            {/* Horizontal stacked bar of risk distribution */}
            <div className="h-2 w-full rounded-full overflow-hidden flex bg-[#0E1013] gap-0.5 mb-2">
              <div
                title={`${criticalAlerts} Critical`}
                style={{ width: `${critPct}%` }}
                className="bg-[#E5484D]"
              />
              <div
                title={`${highAlerts} High`}
                style={{ width: `${highPct}%` }}
                className="bg-[#F76B15]"
              />
              <div
                title={`${mediumAlerts} Medium`}
                style={{ width: `${medPct}%` }}
                className="bg-[#E5A100]"
              />
              <div
                title={`${lowAlerts} Low`}
                style={{ width: `${lowPct}%` }}
                className="bg-[#8B929C]"
              />
            </div>

            {/* One-line formula explanation */}
            <p className="text-[11px] text-[#8B929C] line-clamp-1" title={postureFormula}>
              {postureFormula}
            </p>
          </div>

          <div className="pt-3 mt-3 border-t border-[#252A31] flex items-center justify-between text-[11px]">
            <Link to="/alerts" className="text-[#8B929C] hover:text-[#E6E8EB] flex items-center gap-1 transition-colors">
              <span>{activeAlerts} active alerts requiring response</span>
              <ArrowRight className="w-3 h-3" strokeWidth={1.5} />
            </Link>
            <span className="text-[#E5484D] font-mono text-[10px]">{criticalAlerts} critical</span>
          </div>
        </div>
      </div>

      {/* ========================================================
          ROW 2: "NEEDS ATTENTION" QUEUE (DENSE TABLE) + TOP 5 RISKY
          ======================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Main: Needs attention queue (col-span-8) */}
        <div className="lg:col-span-8 bg-[#15181D] border border-[#252A31] rounded-[6px] overflow-hidden flex flex-col">
          <div className="px-4 py-2.5 border-b border-[#252A31] flex items-center justify-between bg-[#15181D]">
            <div className="flex items-center gap-2">
              <h3 className="text-[13px] font-semibold text-[#E6E8EB]">Needs attention</h3>
              <span className="text-[11px] text-[#8B929C]">· {activeAlerts} open & investigating</span>
            </div>
            <div className="flex items-center gap-3 text-[11px] text-[#8B929C]">
              <span className="hidden sm:inline">Navigate with <kbd className="font-mono px-1 py-0.2 rounded bg-[#0E1013] border border-[#252A31]">j</kbd>/<kbd className="font-mono px-1 py-0.2 rounded bg-[#0E1013] border border-[#252A31]">k</kbd>, <kbd className="font-mono px-1 py-0.2 rounded bg-[#0E1013] border border-[#252A31]">↵</kbd></span>
              <Link to="/alerts" className="text-[#4C8DFF] hover:underline flex items-center gap-1">
                <span>View all</span>
                <ChevronRight className="w-3 h-3" strokeWidth={1.5} />
              </Link>
            </div>
          </div>

          {/* Dense 36px table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[12px] border-collapse">
              <thead className="bg-[#0E1013] text-[#8B929C] sticky top-0 border-b border-[#252A31] text-[11px] select-none">
                <tr className="h-8">
                  <th className="px-3 font-normal w-24">Severity</th>
                  <th className="px-3 font-normal">Alert / Reason</th>
                  <th className="px-3 font-normal">Endpoint</th>
                  <th className="px-3 font-normal w-20">Actor</th>
                  <th className="px-3 font-normal w-24">OWASP</th>
                  <th className="px-3 font-normal w-16">Age</th>
                  <th className="px-3 font-normal w-20 text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#252A31]">
                {queueAlerts.map((alert, idx) => {
                  const isSelected = idx === selectedAlertIdx;
                  const isCritical = alert.severity === 'critical';
                  const isFirstCritical = idx === 0 && isCritical;

                  return (
                    <tr
                      key={alert.alert_id}
                      onClick={() => navigate(`/alerts/${alert.alert_id}`)}
                      onMouseEnter={() => setSelectedAlertIdx(idx)}
                      className={`h-9 cursor-pointer transition-colors ${
                        isSelected ? 'bg-[#1C2026]' : 'hover:bg-[#1C2026]/60'
                      } ${isFirstCritical ? 'border-l-2 border-l-[#E5484D]' : ''}`}
                    >
                      {/* Severity */}
                      <td className="px-3 whitespace-nowrap">
                        <SeverityDot severity={alert.severity} />
                      </td>

                      {/* Reason / Title */}
                      <td className="px-3 font-normal text-[#E6E8EB] max-w-xs truncate" title={alert.reason}>
                        {alert.reason}
                      </td>

                      {/* API route (mono) */}
                      <td className="px-3 font-mono text-[12px] text-[#8B929C] truncate max-w-[180px]">
                        {alert.api}
                      </td>

                      {/* Actor (mono) */}
                      <td className="px-3 font-mono text-[12px] text-[#8B929C] whitespace-nowrap">
                        {alert.actor}
                      </td>

                      {/* OWASP */}
                      <td className="px-3 text-[11px] text-[#8B929C] whitespace-nowrap">
                        {alert.owasp.split(' ')[0]}
                      </td>

                      {/* Age */}
                      <td className="px-3 whitespace-nowrap">
                        <RelativeTime timestamp={alert.last_seen} />
                      </td>

                      {/* Status */}
                      <td className="px-3 text-right whitespace-nowrap">
                        <span
                          className={`text-[11px] px-1.5 py-0.5 rounded-[3px] border ${
                            alert.status === 'open'
                              ? 'text-[#E5484D] border-[#E5484D]/30 bg-[#E5484D]/10'
                              : 'text-[#E5A100] border-[#E5A100]/30 bg-[#E5A100]/10'
                          }`}
                        >
                          {alert.status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Side: Top 5 riskiest APIs (col-span-4) */}
        <div className="lg:col-span-4 bg-[#15181D] border border-[#252A31] rounded-[6px] overflow-hidden flex flex-col justify-between">
          <div>
            <div className="px-4 py-2.5 border-b border-[#252A31] flex items-center justify-between bg-[#15181D]">
              <div>
                <h3 className="text-[13px] font-semibold text-[#E6E8EB]">Top riskiest APIs</h3>
                <span className="text-[11px] text-[#8B929C]">Prioritized by composite score</span>
              </div>
              <Link to="/inventory" className="text-[11px] text-[#4C8DFF] hover:underline flex items-center gap-1">
                <span>All {totalApis}</span>
                <ChevronRight className="w-3 h-3" strokeWidth={1.5} />
              </Link>
            </div>

            <div className="p-3 space-y-2">
              {topRisky.map((api) => {
                const scoreColor = api.risk_score >= 90 ? 'text-[#E5484D]' : api.risk_score >= 75 ? 'text-[#F76B15]' : 'text-[#E5A100]';
                const barColor = api.risk_score >= 90 ? 'bg-[#E5484D]' : api.risk_score >= 75 ? 'bg-[#F76B15]' : 'bg-[#E5A100]';

                return (
                  <Link
                    key={api.api_id}
                    to={`/inventory/${api.api_id}`}
                    className="block p-2 rounded-[4px] hover:bg-[#1C2026] border border-transparent hover:border-[#252A31] transition-colors group"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-1.5 min-w-0">
                        <MethodTag method={api.method} />
                        <span className="font-mono text-[12px] text-[#E6E8EB] group-hover:text-[#4C8DFF] truncate transition-colors">
                          {api.path_template}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5 shrink-0">
                        <span className={`font-mono text-[12px] font-medium ${scoreColor}`}>
                          {api.risk_score}
                        </span>
                        <span className="text-[10px] text-[#8B929C] font-mono">/100</span>
                      </div>
                    </div>

                    {/* Thin score bar */}
                    <div className="h-1 w-full bg-[#0E1013] rounded-full overflow-hidden my-1.5">
                      <div
                        className={`h-full ${barColor}`}
                        style={{ width: `${api.risk_score}%` }}
                      />
                    </div>

                    <div className="text-[11px] text-[#8B929C] line-clamp-1">
                      {api.reason_chip}
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>

          <div className="p-3 border-t border-[#252A31] bg-[#0E1013] text-[11px] text-[#8B929C] flex items-center justify-between">
            <span>Discovered via passive wire traffic</span>
            <Link to="/inventory?status=shadow" className="text-[#B47AEA] hover:underline">
              {shadowCount} shadow endpoints
            </Link>
          </div>
        </div>
      </div>

      {/* ========================================================
          ROW 3: TRAFFIC WITH ALERT ANNOTATIONS + ALERTS BY TYPE
          ======================================================== */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Left: Annotated Traffic Telemetry (col-span-7) */}
        <div className="lg:col-span-7 bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h3 className="text-[13px] font-semibold text-[#E6E8EB]">Traffic volume over time</h3>
              <p className="text-[11px] text-[#8B929C]">Requests per minute with incident window markers</p>
            </div>
            <span className="text-[11px] text-[#8B929C] font-mono">Window: 21:00 - 22:30 UTC</span>
          </div>

          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={miniTraffic} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="mainTrafficGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#4C8DFF" stopOpacity={0.2} />
                    <stop offset="100%" stopColor="#4C8DFF" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="2 2" stroke="#252A31" vertical={false} />
                <XAxis
                  dataKey="timestamp"
                  stroke="#5C626C"
                  tick={{ fontSize: 11, fontFamily: 'JetBrains Mono', fill: '#8B929C' }}
                  tickLine={false}
                  axisLine={{ stroke: '#252A31' }}
                />
                <YAxis
                  stroke="#5C626C"
                  tick={{ fontSize: 11, fontFamily: 'JetBrains Mono', fill: '#8B929C' }}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      const isAlertWindow = data.timestamp === '22:15' || data.timestamp === '22:00';
                      return (
                        <div className="bg-[#15181D] border border-[#252A31] p-2 rounded-[4px] shadow-lg text-[11px] font-mono text-[#E6E8EB]">
                          <div className="text-[#8B929C]">{data.timestamp} UTC</div>
                          <div className="font-semibold text-[#4C8DFF]">{data.count.toLocaleString()} req/min</div>
                          {isAlertWindow && (
                            <div className="text-[#E5484D] mt-1 flex items-center gap-1">
                              <span className="w-1.5 h-1.5 rounded-full bg-[#E5484D]" />
                              <span>BOLA burst anomaly detected</span>
                            </div>
                          )}
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                {/* Shaded anomaly burst window */}
                <ReferenceArea x1="22:00" x2="22:30" fill="#E5484D" fillOpacity={0.08} />
                {/* Vertical marker for attack onset */}
                <ReferenceLine x="22:15" stroke="#E5484D" strokeWidth={1} strokeDasharray="3 3" label={{ value: 'BOLA burst onset', fill: '#E5484D', fontSize: 10, position: 'top' }} />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#4C8DFF"
                  strokeWidth={1.5}
                  fill="url(#mainTrafficGrad)"
                  dot={false}
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="pt-2 mt-2 border-t border-[#252A31] flex items-center justify-between text-[11px] text-[#8B929C]">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-xs bg-[#E5484D]/30 border border-[#E5484D]/60" />
              <span>Shaded region indicates active incident detection window</span>
            </span>
            <Link to="/traffic" className="text-[#4C8DFF] hover:underline">
              Inspect full telemetry →
            </Link>
          </div>
        </div>

        {/* Right: Alerts by type breakdown (col-span-5) */}
        <div className="lg:col-span-5 bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-[13px] font-semibold text-[#E6E8EB]">Alerts by attack type</h3>
                <p className="text-[11px] text-[#8B929C]">Distribution across abuse detector families</p>
              </div>
              <span className="text-[11px] text-[#8B929C] font-mono">15 total</span>
            </div>

            <div className="space-y-2.5">
              {alertTypes.map(item => {
                const maxCount = 5;
                const barWidth = (item.count / maxCount) * 100;

                return (
                  <Link
                    key={item.key}
                    to={`/alerts?type=${item.key}`}
                    className="block group"
                  >
                    <div className="flex items-center justify-between text-[12px] mb-1">
                      <span className="text-[#E6E8EB] group-hover:text-[#4C8DFF] transition-colors">
                        {item.type}
                      </span>
                      <span className="font-mono text-[#8B929C] group-hover:text-[#E6E8EB] transition-colors text-[11px]">
                        {item.count} alerts
                      </span>
                    </div>
                    <div className="h-1.5 w-full bg-[#0E1013] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-[#4C8DFF] group-hover:bg-[#3A7DEE] transition-all"
                        style={{ width: `${barWidth}%` }}
                      />
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>

          <div className="pt-2 mt-2 border-t border-[#252A31] flex items-center justify-between text-[11px] text-[#8B929C]">
            <span>Click any type to filter the alert feed</span>
            <Link to="/evaluation" className="text-[#4C8DFF] hover:underline">
              Detector metrics →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
