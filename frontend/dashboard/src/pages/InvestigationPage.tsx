import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  useAlertQuery,
  useAlertsQuery,
  useAlertRequestsQuery,
  useActorActivityQuery,
  useUpdateAlertStatusMutation,
} from '../api/queries';
import { SeverityDot } from '../components/common/SeverityDot';
import { RelativeTime } from '../components/common/RelativeTime';
import { AlertStatus } from '../types';
import {
  ArrowLeft,
  Download,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Shield,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export const InvestigationPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const alertId = id || 'alt-01';

  const { data: rawAlert, isLoading: alertLoading } = useAlertQuery(alertId);
  const { data: allAlerts = [] } = useAlertsQuery();
  const alert = rawAlert || allAlerts.find((a) => a.alert_id === alertId) || allAlerts[0];

  const { data: requests = [] } = useAlertRequestsQuery(alert?.alert_id || alertId);
  const { data: actorActivity } = useActorActivityQuery(alert?.actor || 'u_17');
  const updateStatusMutation = useUpdateAlertStatusMutation();

  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [copiedCurlId, setCopiedCurlId] = useState<string | null>(null);

  if (alertLoading && !alert) {
    return (
      <div className="space-y-4 animate-pulse select-none">
        <div className="h-28 rounded-2xl bg-white border border-slate-200 shadow-xs" />
        <div className="h-48 rounded-2xl bg-white border border-slate-200 shadow-xs" />
        <div className="h-96 rounded-2xl bg-white border border-slate-200 shadow-xs" />
      </div>
    );
  }

  if (!alert) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-10 text-center space-y-4 shadow-xs select-none">
        <Shield className="w-10 h-10 text-slate-400 mx-auto" strokeWidth={1.5} />
        <h2 className="text-base font-bold text-slate-900">No Security Alerts to Investigate</h2>
        <p className="text-xs text-slate-500">No active forensic anomalies have been reported in this cluster.</p>
        <Link
          to="/alerts"
          className="inline-block mt-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs transition-colors"
        >
          View All Alerts
        </Link>
      </div>
    );
  }

  const handleStatusChange = (newStatus: AlertStatus) => {
    updateStatusMutation.mutate({ id: alert.alert_id, status: newStatus });
  };

  const copyAsCurl = (req: any) => {
    const curl = `curl -X ${req.method} "https://api.bharatpay.internal${req.raw_path}" \\
  -H "Authorization: Bearer ${req.token_id || 'anonymous'}" \\
  -H "User-Agent: ${req.user_agent}" \\
  -H "X-Forwarded-For: ${req.client_ip}"`;
    navigator.clipboard.writeText(curl);
    setCopiedCurlId(req.request_id);
    setTimeout(() => setCopiedCurlId(null), 2000);
  };

  const exportCsv = () => {
    if (!requests || requests.length === 0) return;
    const headers = ['request_id', 'timestamp', 'method', 'raw_path', 'status_code', 'response_size', 'client_ip', 'user_id', 'object_ids'];
    const rows = requests.map((r) => [
      r.request_id,
      r.timestamp,
      r.method,
      `"${r.raw_path}"`,
      r.status_code,
      r.response_size,
      r.client_ip,
      r.user_id || '',
      `"${r.object_ids.join(';')}"`,
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `evidence_${alert.alert_id}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const timelineData = requests.map((r, i) => ({
    time: r.timestamp.split('T')[1]?.slice(0, 8) || `${i * 6}s`,
    latency: r.latency_ms,
    isViolation: i > 0,
  }));

  return (
    <div className="space-y-5 select-none font-sans pb-12">
      {/* 1. Header Bar */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
        <div className="flex items-start gap-3.5">
          <Link
            to="/alerts"
            className="p-2 rounded-xl bg-slate-50 text-slate-500 hover:text-slate-900 border border-slate-200 hover:border-slate-300 transition-colors mt-0.5 shadow-2xs"
            title="Back to alerts"
          >
            <ArrowLeft className="w-4 h-4" strokeWidth={2} />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <SeverityDot severity={alert.severity} />
              <span className="text-xs font-mono text-slate-600 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded-md font-medium">
                {alert.owasp}
              </span>
              <span className="text-xs font-mono text-slate-400">#{alert.alert_id}</span>
            </div>
            <h1 className="text-base font-bold text-slate-900 font-mono mt-1">
              {alert.type}: {alert.api}
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 font-mono mt-1.5">
              <span>Actor: <strong className="text-slate-900">{alert.actor}</strong></span>
              <span>·</span>
              <span>First seen: <RelativeTime timestamp={alert.first_seen} /></span>
              <span>·</span>
              <span>Last seen: <RelativeTime timestamp={alert.last_seen} /></span>
              <span>·</span>
              <Link to="/inventory" className="text-blue-600 hover:underline font-semibold">
                View endpoint details →
              </Link>
            </div>
          </div>
        </div>

        {/* Triage status button group */}
        <div className="flex items-center gap-1.5 bg-slate-100 border border-slate-200 p-1 rounded-xl self-start md:self-center">
          {(['open', 'investigating', 'resolved'] as AlertStatus[]).map((statusOption) => (
            <button
              key={statusOption}
              onClick={() => handleStatusChange(statusOption)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg capitalize transition-all ${
                alert.status === statusOption
                  ? 'bg-white text-blue-700 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {statusOption}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Rationale / Why this fired */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-2 shadow-xs">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-900">
          <AlertCircle className="w-4 h-4 text-red-600 shrink-0" strokeWidth={2} />
          <span>Why this alert fired</span>
        </div>
        <p className="text-sm text-slate-700 leading-relaxed font-normal">
          {alert.reason}
        </p>
        <div className="flex flex-wrap items-center gap-3 pt-2 text-xs text-slate-500 font-mono border-t border-slate-100 mt-2">
          <span>Threshold: baseline is ≤ 2 distinct accounts / session</span>
          <span>·</span>
          <span>Observed: <strong className="text-red-600">{alert.request_ids ? alert.request_ids.length : 1} requests</strong></span>
          <span>·</span>
          <span>Classification: {alert.owasp}</span>
        </div>
      </div>

      {/* Identity Context & Trust Block */}
      {(alert.identity_context || (alert as any).identityContext || alert.reasoning_chain || (alert as any).reasoningChain || alert.priority_tag || (alert as any).priorityTag) && (
        <div className="bg-blue-50/40 border border-blue-200/80 rounded-2xl p-5 space-y-3 shadow-xs">
          <div className="flex items-center justify-between border-b border-blue-100 pb-2.5">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-900">
              <Shield className="w-4 h-4 text-blue-600" />
              <span>Identity & Context Trust Analysis</span>
            </div>
            {(alert.priority_tag || (alert as any).priorityTag) && (
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border uppercase font-bold ${
                alert.is_downgraded || (alert as any).isDowngraded
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : 'bg-red-50 text-red-700 border-red-200'
              }`}>
                {alert.priority_tag || (alert as any).priorityTag}
              </span>
            )}
          </div>

          {/* Context Details Grid */}
          {(alert.identity_context || (alert as any).identityContext) && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs bg-white p-3.5 rounded-xl border border-blue-100 shadow-2xs">
              <div>
                <span className="text-slate-400 text-[11px] block">Privileged Role</span>
                <span className="font-semibold text-slate-900">
                  {alert.identity_context?.role || (alert as any).identityContext?.role || 'VP Sales'}
                </span>
              </div>
              <div>
                <span className="text-slate-400 text-[11px] block">Declared Scope</span>
                <span className="font-mono text-amber-800 font-semibold">
                  {alert.identity_context?.declared_scope || (alert as any).identityContext?.declaredScope || 'org-wide'}
                </span>
              </div>
              <div>
                <span className="text-slate-400 text-[11px] block">Active Campaign</span>
                <span className="font-medium text-emerald-800">
                  {alert.identity_context?.active_campaign || (alert as any).identityContext?.activeCampaign || 'Diwali Sale 2026 (10x)'}
                </span>
              </div>
              <div>
                <span className="text-slate-400 text-[11px] block">Authorized Baseline</span>
                <span className="font-mono text-slate-800 font-semibold">
                  {alert.identity_context?.effective_limit ? `${alert.identity_context.effective_limit}/day` : '5,000/day (Expanded)'}
                </span>
              </div>
            </div>
          )}

          {/* Reasoning Chain */}
          {(alert.reasoning_chain || (alert as any).reasoningChain) && (
            <div className="space-y-1.5 pt-1">
              <span className="text-[11px] font-mono text-slate-500 uppercase font-semibold block">Detection Reasoning Chain:</span>
              <div className="space-y-1 bg-white p-3.5 rounded-xl border border-blue-100 text-xs font-mono text-slate-800 shadow-2xs">
                {(alert.reasoning_chain || (alert as any).reasoningChain).map((step: string, idx: number) => (
                  <div key={idx} className="flex items-start gap-2">
                    <span className="text-blue-600 font-bold">›</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 3. Attack velocity chronology chart */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col justify-between shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Attack Chronology & Latency Velocity</h3>
            <p className="text-xs text-slate-500 mt-0.5">Observed telemetry requests during the anomaly sequence</p>
          </div>
          <span className="text-xs font-mono text-slate-400">{requests.length} evidence samples</span>
        </div>

        <div className="h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timelineData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="evidenceGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#DC2626" stopOpacity={0.15} />
                  <stop offset="100%" stopColor="#DC2626" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
              <XAxis dataKey="time" stroke="#E2E8F0" tick={{ fontSize: 10, fill: '#64748B', fontFamily: 'JetBrains Mono' }} tickLine={false} />
              <YAxis stroke="#E2E8F0" tick={{ fontSize: 10, fill: '#64748B', fontFamily: 'JetBrains Mono' }} tickLine={false} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-white border border-slate-200 p-2.5 rounded-xl text-xs font-mono text-slate-900 shadow-xl">
                        <div className="text-slate-400 text-[10.5px]">Time: {payload[0].payload.time}</div>
                        <div className="text-red-600 font-bold mt-0.5">Latency: {payload[0].value} ms</div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area type="monotone" dataKey="latency" stroke="#DC2626" strokeWidth={2} fill="url(#evidenceGrad)" dot={false} isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4. Pattern Visualisation per Type */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 shadow-xs">
        <h3 className="text-sm font-semibold text-slate-900">Exploit Pattern Analysis ({alert.type})</h3>

        {alert.type === 'BOLA' && (
          <div className="space-y-2 text-xs">
            <p className="text-slate-600">
              Sequence of account object identifiers iterated by actor <code className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-900 border border-slate-200 font-semibold">{alert.actor}</code>:
            </p>
            <div className="flex flex-wrap gap-1.5 font-mono text-xs pt-1">
              <span className="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold shadow-2xs">
                acc_1001 (caller's legitimate account)
              </span>
              {Array.from({ length: 12 }).map((_, i) => (
                <span
                  key={i}
                  className="px-2 py-1 rounded-lg bg-red-50 text-red-700 border border-red-200 font-medium"
                >
                  acc_{2001 + i}
                </span>
              ))}
              <span className="px-2 py-1 text-slate-500 font-mono">+22 more foreign objects</span>
            </div>
          </div>
        )}

        {alert.type === 'token_misuse' && (
          <div className="space-y-2 text-xs">
            <p className="text-slate-600">
              Distinct geographic client IPs utilizing identical bearer token within 15-minute window:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5 font-mono text-xs pt-1">
              {['194.26.29.112 (Tor Exit / NL)', '45.154.255.89 (Russia)', '185.220.101.5 (Germany)', '91.240.118.23 (Seychelles)', '103.21.244.50 (India)'].map((ip, i) => (
                <div key={i} className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 font-semibold shadow-2xs">
                  {ip}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 5. Forensic Requests Table */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
        <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Telemetry Request Logs (Evidence)</h3>
            <span className="text-xs text-slate-500 font-mono">Showing {requests.length} forensic records</span>
          </div>

          <button
            onClick={exportCsv}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-50 border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold shadow-2xs transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" strokeWidth={2} />
            <span>Export CSV</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 text-[11px] select-none font-sans">
              <tr className="h-9">
                <th className="px-4 font-semibold w-24">Timestamp</th>
                <th className="px-4 font-semibold">Method & Path</th>
                <th className="px-4 font-semibold w-16">Status</th>
                <th className="px-4 font-semibold w-20">Size</th>
                <th className="px-4 font-semibold w-28">Client IP</th>
                <th className="px-4 font-semibold">Target Objects</th>
                <th className="px-4 font-semibold w-24 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {requests.slice(0, 30).map((req, idx) => {
                const isViolation = idx > 0;
                const isExpanded = expandedRow === req.request_id;
                return (
                  <React.Fragment key={req.request_id}>
                    <tr
                      onClick={() => setExpandedRow(isExpanded ? null : req.request_id)}
                      className={`h-10 hover:bg-slate-50 cursor-pointer transition-colors ${
                        isViolation ? 'bg-red-50/30' : ''
                      }`}
                    >
                      <td className="px-4 text-slate-500 text-[11px] whitespace-nowrap">
                        {req.timestamp.split('T')[1]?.slice(0, 8)}
                      </td>
                      <td className="px-4 whitespace-nowrap">
                        <span className="text-blue-600 mr-1.5 font-bold">{req.method}</span>
                        <span className="text-slate-800">{req.raw_path}</span>
                      </td>
                      <td className="px-4 whitespace-nowrap">
                        <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold border ${
                          req.status_code === 200
                            ? 'text-emerald-800 border-emerald-200 bg-emerald-50'
                            : 'text-red-700 border-red-200 bg-red-50'
                        }`}>
                          {req.status_code}
                        </span>
                      </td>
                      <td className="px-4 text-slate-500 whitespace-nowrap text-[11px]">
                        {req.response_size} B
                      </td>
                      <td className="px-4 text-slate-600 whitespace-nowrap text-[11px]">
                        {req.client_ip}
                      </td>
                      <td className="px-4 text-[11px]">
                        {req.object_ids.length > 0 ? (
                          <span className={isViolation ? 'text-red-600 font-bold' : 'text-emerald-700 font-semibold'}>
                            {req.object_ids.join(', ')}
                          </span>
                        ) : (
                          <span className="text-slate-400">—</span>
                        )}
                      </td>
                      <td className="px-4 text-right whitespace-nowrap font-sans">
                        <div className="flex items-center justify-end gap-1.5" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => copyAsCurl(req)}
                            className="px-2 py-0.5 rounded border border-slate-200 hover:bg-slate-100 text-[10.5px] font-mono text-slate-600 transition-colors shadow-2xs"
                            title="Copy as cURL"
                          >
                            {copiedCurlId === req.request_id ? 'Copied' : 'cURL'}
                          </button>
                          <button
                            onClick={() => setExpandedRow(isExpanded ? null : req.request_id)}
                            className="p-1 text-slate-400 hover:text-slate-700 rounded hover:bg-slate-100 transition-colors"
                          >
                            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                          </button>
                        </div>
                      </td>
                    </tr>

                    {isExpanded && (
                      <tr className="bg-slate-50/70">
                        <td colSpan={7} className="p-4">
                          <pre className="p-4 rounded-xl bg-slate-900 text-slate-100 text-xs overflow-x-auto whitespace-pre-wrap font-mono shadow-inner">
                            {JSON.stringify(req, null, 2)}
                          </pre>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* 6. Lateral Scope & Attribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 shadow-xs">
          <div className="flex items-center justify-between text-xs font-bold text-slate-900">
            <span>Endpoints Accessed by Actor</span>
            <span className="font-mono text-slate-400 text-[11px]">{actorActivity?.endpoints_hit?.length || 1} routes</span>
          </div>
          <div className="space-y-1.5 font-mono text-xs">
            {actorActivity?.endpoints_hit?.map((ep, i) => (
              <div key={i} className="flex justify-between items-center text-slate-700 p-2.5 rounded-xl bg-slate-50 border border-slate-200/80">
                <span className="text-slate-900 font-semibold">{ep.path_template}</span>
                <span className="text-slate-500">{ep.count} reqs</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 shadow-xs">
          <div className="text-xs font-bold text-slate-900">
            Attribution & Client Fingerprinting
          </div>
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-2 text-xs font-mono text-slate-700">
            <div>Observed IPs: <span className="text-slate-900 font-semibold">{actorActivity?.ip_changes?.join(', ') || '194.26.29.112'}</span></div>
            <div>User-Agent: <span className="text-slate-900 font-semibold break-all">{actorActivity?.user_agents?.[0] || 'python-requests/2.31.0'}</span></div>
          </div>
        </div>
      </div>

      {/* 7. Remediation Action Panel */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-slate-900 mb-1">
            <Shield className="w-4 h-4 text-blue-600" strokeWidth={2} />
            <span>Recommended Mitigation</span>
          </div>
          <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
            {alert.recommendation}
          </p>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={() => handleStatusChange('resolved')}
            className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-xs transition-colors"
          >
            Mark Resolved
          </button>
          <button
            onClick={() => window.alert(`Policy drop applied at gateway proxy for actor ${alert.actor}`)}
            className="px-4 py-2 rounded-xl bg-white border border-red-300 text-red-700 hover:bg-red-50 text-xs font-semibold shadow-2xs transition-colors"
          >
            Enforce Gateway Block
          </button>
        </div>
      </div>
    </div>
  );
};

export default InvestigationPage;
