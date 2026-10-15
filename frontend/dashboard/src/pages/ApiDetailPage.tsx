import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useInventoryItemQuery } from '../api/queries';
import { StatusTag } from '../components/common/StatusTag';
import { MethodTag } from '../components/common/MethodTag';
import { SeverityDot } from '../components/common/SeverityDot';
import { RelativeTime } from '../components/common/RelativeTime';
import { ArrowLeft, AlertCircle } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

export const ApiDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useInventoryItemQuery(id || 'api-01');

  if (isLoading || !data) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-28 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="h-28 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
          <div className="h-28 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
          <div className="h-28 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
          <div className="h-28 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
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

  const hourlyBaseline = baselines?.find(b => b.metric === 'hourly_distribution');
  const hourlyData = hourlyBaseline ? hourlyBaseline.baseline_values.map((baseVal: number, hour: number) => ({
    hour: `${hour}:00`,
    baseline: baseVal,
    live: hourlyBaseline.live_values[hour] || 0,
  })) : [];

  const riskColor =
    item.risk_score >= 90 ? 'text-[#E5484D]' :
    item.risk_score >= 75 ? 'text-[#F76B15]' :
    item.risk_score >= 50 ? 'text-[#E5A100]' : 'text-[#8B929C]';

  return (
    <div className="space-y-4">
      {/* Header bar */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <Link
            to="/inventory"
            className="p-1.5 rounded-[4px] bg-[#0E1013] text-[#8B929C] hover:text-[#E6E8EB] border border-[#252A31] transition-colors mt-0.5"
            title="Back to inventory"
          >
            <ArrowLeft className="w-4 h-4" strokeWidth={1.5} />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <MethodTag method={item.method} />
              <h1 className="text-[15px] font-semibold text-[#E6E8EB] font-mono">{item.path_template}</h1>
              <StatusTag status={item.status} />
            </div>
            <div className="flex flex-wrap items-center gap-3 text-[11px] text-[#8B929C] mt-1 font-mono">
              <span>ID: {item.api_id}</span>
              <span>·</span>
              <span>Exposure: <span className="text-[#E6E8EB] capitalize">{item.exposure}</span></span>
              <span>·</span>
              <span>Auth: <span className="text-[#E6E8EB] capitalize">{item.auth_type}</span></span>
              <span>·</span>
              <span>Requests: <span className="text-[#E6E8EB]">{item.request_count.toLocaleString()}</span></span>
              <span>·</span>
              <span>Last seen: <RelativeTime timestamp={item.last_seen} /></span>
            </div>
          </div>
        </div>

        {/* Risk score */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="text-right">
            <div className="text-[11px] text-[#8B929C]">Risk score</div>
            <div className="flex items-baseline gap-1 font-mono">
              <span className={`text-xl font-bold ${riskColor}`}>{item.risk_score}</span>
              <span className="text-[11px] text-[#8B929C]">/ 100</span>
            </div>
          </div>
        </div>
      </div>

      {/* Rationale notification */}
      <div className="p-3 bg-[#15181D] border border-[#252A31] rounded-[6px] text-[12px] flex items-start gap-2 text-[#8B929C]">
        <AlertCircle className="w-4 h-4 text-[#E5A100] shrink-0 mt-0.5" strokeWidth={1.5} />
        <div>
          <span className="text-[#E6E8EB] font-medium">Status explanation: </span>
          <span>{getStatusExplanation()}</span>
        </div>
      </div>

      {/* Risk Factors Breakdown */}
      <div>
        <h2 className="text-[13px] font-semibold text-[#E6E8EB] mb-2">Composite risk factor breakdown</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {risk?.breakdown?.map((factor) => {
            const pct = Math.round((factor.points / factor.max_points) * 100);
            return (
              <div
                key={factor.factor}
                className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-3 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between text-[11px] text-[#8B929C] mb-1">
                    <span className="text-[#E6E8EB] font-medium">{factor.factor}</span>
                    <span className="font-mono">{factor.points} / {factor.max_points} pts</span>
                  </div>
                  <div className="h-1.5 w-full bg-[#0E1013] rounded-full overflow-hidden my-1.5">
                    <div
                      className="h-full bg-[#4C8DFF]"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
                <p className="text-[11px] text-[#8B929C] mt-2 line-clamp-2">
                  {factor.reason}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Discovered Parameters Table */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] overflow-hidden">
        <div className="px-4 py-2.5 border-b border-[#252A31] bg-[#15181D] flex items-center justify-between">
          <h2 className="text-[13px] font-semibold text-[#E6E8EB]">Discovered request parameters</h2>
          <span className="text-[11px] text-[#8B929C] font-mono">{item.parameters.length} total parameters</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-[12px] border-collapse">
            <thead className="bg-[#0E1013] text-[#8B929C] border-b border-[#252A31] text-[11px] select-none">
              <tr className="h-8">
                <th className="px-3 font-normal">Parameter</th>
                <th className="px-3 font-normal w-28">Location</th>
                <th className="px-3 font-normal w-28">Type</th>
                <th className="px-3 font-normal w-28 text-right">Required</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#252A31]">
              {item.parameters.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-3 py-4 text-center text-[#8B929C]">
                    No path or query parameters defined.
                  </td>
                </tr>
              ) : (
                item.parameters.map((param) => (
                  <tr key={param.name} className="h-9 hover:bg-[#1C2026] transition-colors">
                    <td className="px-3 font-mono text-[12px] text-[#E6E8EB]">{param.name}</td>
                    <td className="px-3 text-[11px] text-[#8B929C] capitalize">{param.in}</td>
                    <td className="px-3 text-[11px] text-[#8B929C] font-mono">{param.type}</td>
                    <td className="px-3 text-right text-[11px]">
                      {param.required ? (
                        <span className="text-[#E5A100]">Yes</span>
                      ) : (
                        <span className="text-[#5C626C]">No</span>
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
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Baseline comparison chart (col-span-7) */}
        <div className="lg:col-span-7 bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-[13px] font-semibold text-[#E6E8EB]">Hourly traffic baseline vs live observed</h3>
                <p className="text-[11px] text-[#8B929C]">Model baseline distribution compared against current hourly traffic</p>
              </div>
            </div>

            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={hourlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="2 2" stroke="#252A31" vertical={false} />
                  <XAxis dataKey="hour" stroke="#5C626C" tick={{ fontSize: 10, fill: '#8B929C', fontFamily: 'JetBrains Mono' }} tickLine={false} />
                  <YAxis stroke="#5C626C" tick={{ fontSize: 10, fill: '#8B929C', fontFamily: 'JetBrains Mono' }} tickLine={false} />
                  <Tooltip
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-[#15181D] border border-[#252A31] p-2 rounded-[4px] text-[11px] font-mono text-[#E6E8EB]">
                            <div>Hour: {payload[0].payload.hour}</div>
                            <div className="text-[#8B929C]">Baseline: {payload[0].value}</div>
                            <div className="text-[#4C8DFF]">Observed: {payload[1]?.value || 0}</div>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar dataKey="baseline" fill="#3A424E" radius={[2, 2, 0, 0]} name="Baseline" />
                  <Bar dataKey="live" fill="#4C8DFF" radius={[2, 2, 0, 0]} name="Live" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="pt-2 mt-2 border-t border-[#252A31] flex items-center justify-between text-[11px] text-[#8B929C]">
            <span>Baseline computed over 30-day moving window</span>
            <span className="font-mono">Metric: hourly_distribution</span>
          </div>
        </div>

        {/* Related alerts list (col-span-5) */}
        <div className="lg:col-span-5 bg-[#15181D] border border-[#252A31] rounded-[6px] overflow-hidden flex flex-col justify-between">
          <div>
            <div className="px-4 py-2.5 border-b border-[#252A31] flex items-center justify-between bg-[#15181D]">
              <h3 className="text-[13px] font-semibold text-[#E6E8EB]">Related threat alerts</h3>
              <span className="text-[11px] text-[#8B929C] font-mono">{related_alerts?.length || 0} alerts</span>
            </div>

            <div className="divide-y divide-[#252A31]">
              {!related_alerts || related_alerts.length === 0 ? (
                <div className="p-6 text-center text-[#8B929C] text-[12px]">
                  No active abuse alerts associated with this endpoint.
                </div>
              ) : (
                related_alerts.map((alt) => (
                  <Link
                    key={alt.alert_id}
                    to={`/alerts/${alt.alert_id}`}
                    className="p-3 block hover:bg-[#1C2026] transition-colors"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <SeverityDot severity={alt.severity} />
                        <span className="text-[12px] font-medium text-[#E6E8EB]">{alt.type}</span>
                      </div>
                      <RelativeTime timestamp={alt.last_seen} />
                    </div>
                    <p className="text-[11px] text-[#8B929C] line-clamp-1">{alt.reason}</p>
                    <div className="text-[10px] text-[#5C626C] font-mono mt-1">Actor: {alt.actor} · {alt.owasp}</div>
                  </Link>
                ))
              )}
            </div>
          </div>

          <div className="p-3 border-t border-[#252A31] bg-[#0E1013] text-[11px] text-[#8B929C] flex items-center justify-between">
            <span>Click alert to open forensic investigation</span>
            <Link to="/alerts" className="text-[#4C8DFF] hover:underline">
              All alerts →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
