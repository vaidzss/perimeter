import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  useAlertQuery,
  useAlertsQuery,
  useAlertRequestsQuery,
  useActorActivityQuery,
  useUpdateAlertStatusMutation
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
  Shield
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

export const InvestigationPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const alertId = id || 'alt-01';

  const { data: rawAlert, isLoading: alertLoading } = useAlertQuery(alertId);
  const { data: allAlerts = [] } = useAlertsQuery();
  const alert = rawAlert || allAlerts.find(a => a.alert_id === alertId) || allAlerts[0];

  const { data: requests = [] } = useAlertRequestsQuery(alert?.alert_id || alertId);
  const { data: actorActivity } = useActorActivityQuery(alert?.actor || 'u_17');
  const updateStatusMutation = useUpdateAlertStatusMutation();

  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [copiedCurlId, setCopiedCurlId] = useState<string | null>(null);

  if (alertLoading && !alert) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-28 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
        <div className="h-48 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
        <div className="h-96 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
      </div>
    );
  }

  if (!alert) {
    return (
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-8 text-center space-y-3">
        <Shield className="w-8 h-8 text-[#8B929C] mx-auto" strokeWidth={1.5} />
        <h2 className="text-[15px] font-semibold text-[#E6E8EB]">No Security Alerts to Investigate</h2>
        <p className="text-[13px] text-[#8B929C]">No active forensic anomalies have been reported in this cluster.</p>
        <Link to="/alerts" className="inline-block mt-2 px-3 py-1.5 rounded-[4px] bg-[#4C8DFF] text-white text-[12px] font-medium">
          View All Alerts
        </Link>
      </div>
    );
  }

  const handleStatusChange = (newStatus: AlertStatus) => {
    updateStatusMutation.mutate({ id: alert.alert_id, status: newStatus });
  };

  const copyAsCurl = (req: any) => {
    const curl = `curl -X ${req.method} "https://api.cybercup.corp${req.raw_path}" \\
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
    const rows = requests.map(r => [
      r.request_id,
      r.timestamp,
      r.method,
      `"${r.raw_path}"`,
      r.status_code,
      r.response_size,
      r.client_ip,
      r.user_id || '',
      `"${r.object_ids.join(';')}"`
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
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
    <div className="space-y-4">
      {/* 1. Header Bar */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <Link
            to="/alerts"
            className="p-1.5 rounded-[4px] bg-[#0E1013] text-[#8B929C] hover:text-[#E6E8EB] border border-[#252A31] transition-colors mt-0.5"
            title="Back to alerts"
          >
            <ArrowLeft className="w-4 h-4" strokeWidth={1.5} />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <SeverityDot severity={alert.severity} />
              <span className="text-[11px] font-mono text-[#8B929C] border border-[#252A31] px-1.5 py-0.2 rounded-[3px]">
                {alert.owasp}
              </span>
              <span className="text-[11px] font-mono text-[#8B929C]">#{alert.alert_id}</span>
            </div>
            <h1 className="text-[15px] font-semibold text-[#E6E8EB] font-mono mt-1">
              {alert.type}: {alert.api}
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-[11px] text-[#8B929C] font-mono mt-1">
              <span>Actor: <span className="text-[#E6E8EB]">{alert.actor}</span></span>
              <span>·</span>
              <span>First seen: <RelativeTime timestamp={alert.first_seen} /></span>
              <span>·</span>
              <span>Last seen: <RelativeTime timestamp={alert.last_seen} /></span>
              <span>·</span>
              <Link to="/inventory/api-01" className="text-[#4C8DFF] hover:underline">
                View endpoint details →
              </Link>
            </div>
          </div>
        </div>

        {/* Triage status button group */}
        <div className="flex items-center gap-1.5 bg-[#0E1013] border border-[#252A31] p-1 rounded-[6px] self-start md:self-center">
          {(['open', 'investigating', 'resolved'] as AlertStatus[]).map((statusOption) => (
            <button
              key={statusOption}
              onClick={() => handleStatusChange(statusOption)}
              className={`px-2.5 py-1 text-[11px] font-medium rounded-[4px] capitalize transition-colors ${
                alert.status === statusOption
                  ? 'bg-[#15181D] text-[#E6E8EB] border border-[#343B45] shadow-xs'
                  : 'text-[#8B929C] hover:text-[#E6E8EB]'
              }`}
            >
              {statusOption}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Rationale / Why this fired */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 space-y-2">
        <div className="flex items-center gap-2 text-[12px] font-medium text-[#E6E8EB]">
          <AlertCircle className="w-4 h-4 text-[#E5484D] shrink-0" strokeWidth={1.5} />
          <span>Why this alert fired</span>
        </div>
        <p className="text-[13px] text-[#E6E8EB] leading-relaxed">
          {alert.reason}
        </p>
        <div className="flex flex-wrap items-center gap-3 pt-1 text-[11px] text-[#8B929C] font-mono">
          <span>Threshold: baseline is ≤ 2 distinct accounts / session</span>
          <span>·</span>
          <span>Observed: <strong className="text-[#E5484D]">{alert.request_ids ? alert.request_ids.length : 1} requests</strong></span>
          <span>·</span>
          <span>Classification: {alert.owasp}</span>
        </div>
      </div>

      {/* Identity Context & Trust Block (Checkpoint 16) */}
      {(alert.identity_context || (alert as any).identityContext || alert.reasoning_chain || (alert as any).reasoningChain || alert.priority_tag || (alert as any).priorityTag) && (
        <div className="bg-[#171B22] border border-[#2D333F] rounded-[6px] p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-[#252A31] pb-2">
            <div className="flex items-center gap-2 text-[13px] font-semibold text-[#E6E8EB]">
              <Shield className="w-4 h-4 text-indigo-400" />
              <span>Identity & Context Trust Analysis</span>
            </div>
            {(alert.priority_tag || (alert as any).priorityTag) && (
              <span className={`text-[11px] font-mono px-2 py-0.5 rounded border uppercase ${
                alert.is_downgraded || (alert as any).isDowngraded
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  : 'bg-red-500/10 text-red-400 border-red-500/20'
              }`}>
                {alert.priority_tag || (alert as any).priorityTag}
              </span>
            )}
          </div>

          {/* Context Details Grid */}
          {(alert.identity_context || (alert as any).identityContext) && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[12px] bg-[#0E1013] p-3 rounded-[6px] border border-[#252A31]">
              <div>
                <span className="text-[#8B929C] text-[11px] block">Privileged Role</span>
                <span className="font-semibold text-indigo-300">
                  {alert.identity_context?.role || (alert as any).identityContext?.role || 'VP Sales'}
                </span>
              </div>
              <div>
                <span className="text-[#8B929C] text-[11px] block">Declared Scope</span>
                <span className="font-mono text-amber-300">
                  {alert.identity_context?.declared_scope || (alert as any).identityContext?.declaredScope || 'org-wide'}
                </span>
              </div>
              <div>
                <span className="text-[#8B929C] text-[11px] block">Active Campaign</span>
                <span className="font-medium text-emerald-400">
                  {alert.identity_context?.active_campaign || (alert as any).identityContext?.activeCampaign || 'Diwali Sale 2026 (10x)'}
                </span>
              </div>
              <div>
                <span className="text-[#8B929C] text-[11px] block">Authorized Baseline</span>
                <span className="font-mono text-white">
                  {alert.identity_context?.effective_limit ? `${alert.identity_context.effective_limit}/day` : '5,000/day (Expanded)'}
                </span>
              </div>
            </div>
          )}

          {/* Reasoning Chain */}
          {(alert.reasoning_chain || (alert as any).reasoningChain) && (
            <div className="space-y-1.5 pt-1">
              <span className="text-[11px] font-mono text-[#8B929C] uppercase block">Detection Reasoning Chain:</span>
              <div className="space-y-1 bg-[#121419] p-3 rounded-[5px] border border-[#252A31] text-[12px] font-mono text-[#C9CDD3]">
                {(alert.reasoning_chain || (alert as any).reasoningChain).map((step: string, idx: number) => (
                  <div key={idx} className="flex items-start gap-2">
                    <span className="text-indigo-400 font-bold">›</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 3. Attack velocity chronology chart */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col justify-between">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-[13px] font-semibold text-[#E6E8EB]">Attack chronology & latency velocity</h3>
            <p className="text-[11px] text-[#8B929C]">Observed telemetry requests during the anomaly sequence</p>
          </div>
          <span className="text-[11px] font-mono text-[#8B929C]">{requests.length} evidence samples</span>
        </div>

        <div className="h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timelineData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="evidenceGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#E5484D" stopOpacity={0.25} />
                  <stop offset="100%" stopColor="#E5484D" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="2 2" stroke="#252A31" vertical={false} />
              <XAxis dataKey="time" stroke="#5C626C" tick={{ fontSize: 10, fill: '#8B929C', fontFamily: 'JetBrains Mono' }} tickLine={false} />
              <YAxis stroke="#5C626C" tick={{ fontSize: 10, fill: '#8B929C', fontFamily: 'JetBrains Mono' }} tickLine={false} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-[#15181D] border border-[#252A31] p-2 rounded-[4px] text-[11px] font-mono text-[#E6E8EB]">
                        <div>Time: {payload[0].payload.time}</div>
                        <div className="text-[#E5484D]">Latency: {payload[0].value} ms</div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area type="monotone" dataKey="latency" stroke="#E5484D" strokeWidth={1.5} fill="url(#evidenceGrad)" dot={false} isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4. Pattern Visualisation per Type */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 space-y-2">
        <h3 className="text-[13px] font-semibold text-[#E6E8EB]">Exploit pattern analysis ({alert.type})</h3>

        {alert.type === 'BOLA' && (
          <div className="space-y-2 text-[12px]">
            <p className="text-[#8B929C]">
              Sequence of account object identifiers iterated by actor <code className="font-mono text-[#E6E8EB]">{alert.actor}</code>:
            </p>
            <div className="flex flex-wrap gap-1 font-mono text-[11px]">
              <span className="px-2 py-0.5 rounded-[3px] bg-[#10b981]/10 text-[#10b981] border border-[#10b981]/30 font-medium">
                acc_1001 (caller's legitimate account)
              </span>
              {Array.from({ length: 24 }).map((_, i) => (
                <span
                  key={i}
                  className="px-1.5 py-0.5 rounded-[3px] bg-[#E5484D]/10 text-[#E5484D] border border-[#E5484D]/25"
                >
                  acc_{2001 + i}
                </span>
              ))}
              <span className="px-1.5 py-0.5 text-[#8B929C]">+22 more foreign objects</span>
            </div>
          </div>
        )}

        {alert.type === 'token_misuse' && (
          <div className="space-y-2 text-[12px]">
            <p className="text-[#8B929C]">
              Distinct geographic client IPs utilizing identical bearer token within 15-minute window:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2 font-mono text-[11px]">
              {['194.26.29.112 (Tor Exit / NL)', '45.154.255.89 (Russia)', '185.220.101.5 (Germany)', '91.240.118.23 (Seychelles)', '103.21.244.50 (India)'].map((ip, i) => (
                <div key={i} className="p-2 rounded-[4px] bg-[#0E1013] border border-[#252A31] text-[#E5484D]">
                  {ip}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 5. Forensic Requests Table */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] overflow-hidden">
        <div className="px-4 py-2.5 border-b border-[#252A31] flex items-center justify-between bg-[#15181D]">
          <div>
            <h3 className="text-[13px] font-semibold text-[#E6E8EB]">Telemetry request logs (Evidence)</h3>
            <span className="text-[11px] text-[#8B929C]">Showing {requests.length} forensic records</span>
          </div>

          <button
            onClick={exportCsv}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-[4px] bg-[#0E1013] border border-[#252A31] hover:border-[#343B45] text-[#8B929C] hover:text-[#E6E8EB] text-[11px] font-medium transition-colors"
          >
            <Download className="w-3.5 h-3.5" strokeWidth={1.5} />
            <span>Export CSV</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-[12px] border-collapse font-mono">
            <thead className="bg-[#0E1013] text-[#8B929C] border-b border-[#252A31] text-[11px] select-none font-sans">
              <tr className="h-8">
                <th className="px-3 font-normal w-24">Timestamp</th>
                <th className="px-3 font-normal">Method & path</th>
                <th className="px-3 font-normal w-16">Status</th>
                <th className="px-3 font-normal w-20">Size</th>
                <th className="px-3 font-normal w-28">Client IP</th>
                <th className="px-3 font-normal">Target objects</th>
                <th className="px-3 font-normal w-24 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#252A31]">
              {requests.slice(0, 30).map((req, idx) => {
                const isViolation = idx > 0;
                const isExpanded = expandedRow === req.request_id;
                return (
                  <React.Fragment key={req.request_id}>
                    <tr
                      onClick={() => setExpandedRow(isExpanded ? null : req.request_id)}
                      className={`h-9 hover:bg-[#1C2026] cursor-pointer transition-colors ${
                        isViolation ? 'bg-[#E5484D]/5' : ''
                      }`}
                    >
                      <td className="px-3 text-[#8B929C] text-[11px] whitespace-nowrap">
                        {req.timestamp.split('T')[1]?.slice(0, 8)}
                      </td>
                      <td className="px-3 whitespace-nowrap">
                        <span className="text-[#4C8DFF] mr-1.5 font-medium">{req.method}</span>
                        <span className="text-[#E6E8EB]">{req.raw_path}</span>
                      </td>
                      <td className="px-3 whitespace-nowrap">
                        <span className={`text-[11px] px-1.5 py-0.2 rounded-[3px] border ${
                          req.status_code === 200
                            ? 'text-[#10b981] border-[#10b981]/30 bg-[#10b981]/10'
                            : 'text-[#E5484D] border-[#E5484D]/30 bg-[#E5484D]/10'
                        }`}>
                          {req.status_code}
                        </span>
                      </td>
                      <td className="px-3 text-[#8B929C] whitespace-nowrap text-[11px]">
                        {req.response_size} B
                      </td>
                      <td className="px-3 text-[#8B929C] whitespace-nowrap text-[11px]">
                        {req.client_ip}
                      </td>
                      <td className="px-3 text-[11px]">
                        {req.object_ids.length > 0 ? (
                          <span className={isViolation ? 'text-[#E5484D]' : 'text-[#10b981]'}>
                            {req.object_ids.join(', ')}
                          </span>
                        ) : (
                          <span className="text-[#5C626C]">—</span>
                        )}
                      </td>
                      <td className="px-3 text-right whitespace-nowrap font-sans">
                        <div className="flex items-center justify-end gap-1.5" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => copyAsCurl(req)}
                            className="px-2 py-0.5 rounded-[3px] border border-[#252A31] hover:bg-[#1C2026] text-[11px] text-[#8B929C] hover:text-[#E6E8EB] transition-colors"
                            title="Copy as cURL"
                          >
                            {copiedCurlId === req.request_id ? 'Copied' : 'cURL'}
                          </button>
                          <button
                            onClick={() => setExpandedRow(isExpanded ? null : req.request_id)}
                            className="p-1 text-[#8B929C] hover:text-[#E6E8EB]"
                          >
                            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                          </button>
                        </div>
                      </td>
                    </tr>

                    {isExpanded && (
                      <tr className="bg-[#0E1013]">
                        <td colSpan={7} className="p-3">
                          <pre className="p-3 rounded-[4px] bg-[#15181D] border border-[#252A31] text-[11px] text-[#4C8DFF] overflow-x-auto whitespace-pre-wrap font-mono">
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 space-y-2">
          <div className="flex items-center justify-between text-[12px] font-medium text-[#E6E8EB]">
            <span>Endpoints accessed by actor</span>
            <span className="font-mono text-[#8B929C] text-[11px]">{actorActivity?.endpoints_hit?.length || 1} routes</span>
          </div>
          <div className="space-y-1.5 font-mono text-[11px]">
            {actorActivity?.endpoints_hit?.map((ep, i) => (
              <div key={i} className="flex justify-between items-center text-[#8B929C] p-2 rounded-[4px] bg-[#0E1013] border border-[#252A31]">
                <span className="text-[#E6E8EB]">{ep.path_template}</span>
                <span>{ep.count} reqs</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 space-y-2">
          <div className="text-[12px] font-medium text-[#E6E8EB]">
            Attribution & fingerprinting
          </div>
          <div className="p-3 rounded-[4px] bg-[#0E1013] border border-[#252A31] space-y-1 text-[11px] font-mono text-[#8B929C]">
            <div>Observed IPs: <span className="text-[#E6E8EB]">{actorActivity?.ip_changes?.join(', ') || '194.26.29.112'}</span></div>
            <div>User-Agent: <span className="text-[#E6E8EB] break-all">{actorActivity?.user_agents?.[0] || 'python-requests/2.31.0'}</span></div>
          </div>
        </div>
      </div>

      {/* 7. Remediation Action Panel */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-1.5 text-[12px] font-medium text-[#E6E8EB] mb-1">
            <Shield className="w-4 h-4 text-[#4C8DFF]" strokeWidth={1.5} />
            <span>Recommended mitigation</span>
          </div>
          <p className="text-[12px] text-[#8B929C] max-w-2xl">
            {alert.recommendation}
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={() => handleStatusChange('resolved')}
            className="px-3 py-1.5 rounded-[4px] bg-[#10b981] hover:bg-[#059669] text-white text-[12px] font-medium transition-colors"
          >
            Mark resolved
          </button>
          <button
            onClick={() => window.alert(`Policy drop applied at gateway proxy for actor ${alert.actor}`)}
            className="px-3 py-1.5 rounded-[4px] bg-[#0E1013] border border-[#E5484D]/40 text-[#E5484D] hover:bg-[#E5484D]/10 text-[12px] font-medium transition-colors"
          >
            Enforce gateway block
          </button>
        </div>
      </div>
    </div>
  );
};
