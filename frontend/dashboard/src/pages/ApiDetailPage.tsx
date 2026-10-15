import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useInventoryItemQuery } from '../api/queries';
import { StatusTag } from '../components/common/StatusTag';
import { MethodTag } from '../components/common/MethodTag';
import { SeverityDot } from '../components/common/SeverityDot';
import { RelativeTime } from '../components/common/RelativeTime';
import { ArrowLeft, AlertCircle, ArrowRight } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export const ApiDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useInventoryItemQuery(id || 'api-01');

  if (isLoading || !data) {
    return (
      <div className="space-y-4 animate-pulse select-none">
        <div className="h-28 rounded-2xl bg-white border border-slate-200 shadow-xs" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="h-28 rounded-xl bg-white border border-slate-200 shadow-xs" />
          <div className="h-28 rounded-xl bg-white border border-slate-200 shadow-xs" />
          <div className="h-28 rounded-xl bg-white border border-slate-200 shadow-xs" />
          <div className="h-28 rounded-xl bg-white border border-slate-200 shadow-xs" />
        </div>
      </div>
    );
  }

  const { inventory_item: item, risk_breakdown: risk, baselines, related_alerts } = data;

  const getStatusExplanation = () => {
    switch (item.status) {
      case 'shadow':
        return `Discovered in wire traffic with ${item.request_count.toLocaleString()} observed requests, but completely absent from openapi.yaml repository.`;
      case 'zombie':
        return `Endpoint was marked as deprecated in OpenAPI spec 12 months ago, but still receiving active production calls with basic credentials.`;
      case 'unmanaged':
        return `Third-party webhook bypasses the Envoy gateway proxy and directly addresses the application cluster.`;
      case 'unused_documented':
        return `Documented in openapi.yaml, but only 3 requests observed in the last 60 days.`;
      case 'documented':
      default:
        return `Fully registered and tracked in openapi.yaml repository with synchronized parameter models.`;
    }
  };

  const hourlyBaseline = baselines?.find((b) => b.metric === 'hourly_distribution');
  const hourlyData = hourlyBaseline
    ? hourlyBaseline.baseline_values.map((baseVal: number, hour: number) => ({
        hour: `${hour}:00`,
        baseline: baseVal,
        live: hourlyBaseline.live_values[hour] || 0,
      }))
    : [];

  const riskColor =
    item.risk_score >= 90
      ? 'text-red-700'
      : item.risk_score >= 75
      ? 'text-amber-800'
      : item.risk_score >= 50
      ? 'text-yellow-800'
      : 'text-slate-600';

  return (
    <div className="space-y-5 select-none font-sans pb-12">
      {/* Header bar */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
        <div className="flex items-start gap-3.5">
          <Link
            to="/inventory"
            className="p-2 rounded-xl bg-slate-50 text-slate-500 hover:text-slate-900 border border-slate-200 hover:border-slate-300 transition-colors mt-0.5 shadow-2xs"
            title="Back to inventory"
          >
            <ArrowLeft className="w-4 h-4" strokeWidth={2} />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <MethodTag method={item.method} />
              <h1 className="text-base font-bold text-slate-900 font-mono">{item.path_template}</h1>
              <StatusTag status={item.status} />
            </div>
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 mt-1.5 font-mono">
              <span>ID: <strong className="text-slate-800">{item.api_id}</strong></span>
              <span>·</span>
              <span>Exposure: <span className="text-slate-800 capitalize font-medium">{item.exposure}</span></span>
              <span>·</span>
              <span>Auth: <span className="text-slate-800 capitalize font-medium">{item.auth_type}</span></span>
              <span>·</span>
              <span>Requests: <span className="text-slate-800 font-medium">{item.request_count.toLocaleString()}</span></span>
              <span>·</span>
              <span>Last seen: <RelativeTime timestamp={item.last_seen} /></span>
            </div>
          </div>
        </div>

        {/* Risk score */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="text-right">
            <div className="text-xs text-slate-400 font-mono">Risk score</div>
            <div className="flex items-baseline gap-1 font-mono">
              <span className={`text-2xl font-bold ${riskColor}`}>{item.risk_score}</span>
              <span className="text-xs text-slate-400">/ 100</span>
            </div>
          </div>
        </div>
      </div>

      {/* Rationale notification */}
      <div className="p-4 bg-amber-50/70 border border-amber-200/80 rounded-2xl text-xs flex items-start gap-2.5 text-amber-900 shadow-2xs">
        <AlertCircle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" strokeWidth={2} />
        <div>
          <span className="font-bold text-amber-950">Status explanation: </span>
          <span>{getStatusExplanation()}</span>
        </div>
      </div>

      {/* Risk Factors Breakdown */}
      <div>
        <h2 className="text-sm font-semibold text-slate-900 mb-2.5">Composite Risk Factor Breakdown</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {risk?.breakdown?.map((factor) => {
            const pct = Math.round((factor.points / factor.max_points) * 100);
            return (
              <div
                key={factor.factor}
                className="bg-white border border-slate-200 rounded-xl p-4 flex flex-col justify-between shadow-2xs"
              >
                <div>
                  <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                    <span className="text-slate-900 font-bold">{factor.factor}</span>
                    <span className="font-mono text-[11px]">{factor.points} / {factor.max_points} pts</span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden my-2">
                    <div
                      className="h-full bg-blue-600 rounded-full"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
                <p className="text-xs text-slate-600 mt-2 line-clamp-2 leading-relaxed">
                  {factor.reason}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Discovered Parameters Table */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
        <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-900">Discovered Request Parameters</h2>
          <span className="text-xs text-slate-400 font-mono">{item.parameters.length} total parameters</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 text-[11px] select-none font-sans">
              <tr className="h-9">
                <th className="px-4 font-semibold">Parameter</th>
                <th className="px-4 font-semibold w-28">Location</th>
                <th className="px-4 font-semibold w-28">Type</th>
                <th className="px-4 font-semibold w-28 text-right">Required</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {item.parameters.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-slate-400 font-mono">
                    No path or query parameters defined.
                  </td>
                </tr>
              ) : (
                item.parameters.map((param) => (
                  <tr key={param.name} className="h-10 hover:bg-slate-50 transition-colors">
                    <td className="px-4 font-mono text-xs text-slate-900 font-semibold">{param.name}</td>
                    <td className="px-4 text-xs text-slate-600 capitalize">{param.in}</td>
                    <td className="px-4 text-xs text-slate-600 font-mono">{param.type}</td>
                    <td className="px-4 text-right text-xs">
                      {param.required ? (
                        <span className="text-amber-800 font-semibold bg-amber-50 px-2 py-0.5 rounded border border-amber-200">Yes</span>
                      ) : (
                        <span className="text-slate-400">No</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Baseline Comparison Chart & Related Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Baseline comparison chart (col-span-7) */}
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-2xl p-5 flex flex-col justify-between shadow-xs">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-slate-900">Hourly Traffic Baseline vs Live Observed</h3>
                <p className="text-xs text-slate-500 mt-0.5">Model baseline distribution compared against current hourly traffic</p>
              </div>
            </div>

            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={hourlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                  <XAxis dataKey="hour" stroke="#E2E8F0" tick={{ fontSize: 10, fill: '#64748B', fontFamily: 'JetBrains Mono' }} tickLine={false} />
                  <YAxis stroke="#E2E8F0" tick={{ fontSize: 10, fill: '#64748B', fontFamily: 'JetBrains Mono' }} tickLine={false} />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-white border border-slate-200 p-3 rounded-xl text-xs font-mono text-slate-900 shadow-xl">
                            <div className="text-slate-400 text-[10.5px]">Hour: {payload[0].payload.hour}</div>
                            <div className="text-slate-500 mt-1">Baseline: {payload[0].value}</div>
                            <div className="text-blue-600 font-bold">Observed: {payload[1]?.value || 0}</div>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="baseline" fill="#CBD5E1" radius={[3, 3, 0, 0]} name="Baseline" />
                  <Bar dataKey="live" fill="#2563EB" radius={[3, 3, 0, 0]} name="Live" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="pt-3 mt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500 font-mono">
            <span>Baseline computed over 30-day moving window</span>
            <span>Metric: hourly_distribution</span>
          </div>
        </div>

        {/* Related alerts list (col-span-5) */}
        <div className="lg:col-span-5 bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs flex flex-col justify-between">
          <div>
            <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-900">Related Threat Alerts</h3>
              <span className="text-xs text-slate-400 font-mono">{related_alerts?.length || 0} alerts</span>
            </div>

            <div className="divide-y divide-slate-100">
              {!related_alerts || related_alerts.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-xs font-mono">
                  No active abuse alerts associated with this endpoint.
                </div>
              ) : (
                related_alerts.map((alt) => (
                  <Link
                    key={alt.alert_id}
                    to={`/alerts/${alt.alert_id}`}
                    className="p-3.5 block hover:bg-slate-50 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <SeverityDot severity={alt.severity} />
                        <span className="text-xs font-bold text-slate-900">{alt.type}</span>
                      </div>
                      <RelativeTime timestamp={alt.last_seen} />
                    </div>
                    <p className="text-xs text-slate-600 line-clamp-1 mt-1">{alt.reason}</p>
                    <div className="text-[11px] text-slate-400 font-mono mt-1">Actor: {alt.actor} · {alt.owasp}</div>
                  </Link>
                ))
              )}
            </div>
          </div>

          <div className="p-4 border-t border-slate-100 bg-slate-50 text-xs text-slate-600 flex items-center justify-between font-mono">
            <span>Click alert to open forensic evidence</span>
            <Link to="/alerts" className="text-blue-600 font-bold hover:underline flex items-center gap-1">
              <span>All alerts</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApiDetailPage;
