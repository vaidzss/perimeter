import React, { useState } from 'react';
import { useTrafficStatsQuery } from '../api/queries';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

export const TrafficPage: React.FC = () => {
  const [window, setWindow] = useState('1h');
  const { data: stats, isLoading } = useTrafficStatsQuery(window);

  if (isLoading || !stats) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-14 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-20 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
          ))}
        </div>
        <div className="h-64 rounded-[6px] bg-[#15181D] border border-[#252A31]" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header and window picker */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-[15px] font-semibold text-[#E6E8EB]">Traffic telemetry & baselines</h1>
          <p className="text-[12px] text-[#8B929C] mt-0.5">
            Ingress gateway telemetry, latency percentiles, error rates, and top consumer attribution
          </p>
        </div>

        {/* Time window selector */}
        <div className="flex items-center gap-1 bg-[#0E1013] border border-[#252A31] p-1 rounded-[6px] text-[11px] self-start md:self-center font-mono">
          {['15m', '1h', '6h', '24h'].map((w) => (
            <button
              key={w}
              onClick={() => setWindow(w)}
              className={`px-2.5 py-1 rounded-[4px] transition-colors ${
                window === w
                  ? 'bg-[#15181D] text-[#E6E8EB] border border-[#343B45] font-medium shadow-xs'
                  : 'text-[#8B929C] hover:text-[#E6E8EB]'
              }`}
            >
              {w}
            </button>
          ))}
        </div>
      </div>

      {/* Latency & Error Rate Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-3">
          <span className="text-[11px] text-[#8B929C]">p50 Latency</span>
          <div className="text-xl font-semibold text-[#E6E8EB] font-mono mt-0.5">{stats.latency_percentiles.p50} ms</div>
          <span className="text-[11px] text-[#10b981]">Baseline compliant</span>
        </div>

        <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-3">
          <span className="text-[11px] text-[#8B929C]">p90 Latency</span>
          <div className="text-xl font-semibold text-[#E6E8EB] font-mono mt-0.5">{stats.latency_percentiles.p90} ms</div>
          <span className="text-[11px] text-[#8B929C]">Nominal SLA</span>
        </div>

        <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-3">
          <span className="text-[11px] text-[#8B929C]">p99 Latency</span>
          <div className="text-xl font-semibold text-[#E6E8EB] font-mono mt-0.5">{stats.latency_percentiles.p99} ms</div>
          <span className="text-[11px] text-[#8B929C]">Spike ceiling</span>
        </div>

        <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-3">
          <span className="text-[11px] text-[#8B929C]">4xx Error rate</span>
          <div className="text-xl font-semibold text-[#E5484D] font-mono mt-0.5">{stats.error_rates.rate_4xx}%</div>
          <span className="text-[11px] text-[#E5484D]">Elevated client probes</span>
        </div>

        <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-3">
          <span className="text-[11px] text-[#8B929C]">5xx Error rate</span>
          <div className="text-xl font-semibold text-[#E6E8EB] font-mono mt-0.5">{stats.error_rates.rate_5xx}%</div>
          <span className="text-[11px] text-[#10b981]">0 unhandled crashes</span>
        </div>
      </div>

      {/* Requests over time chart */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col justify-between">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-[13px] font-semibold text-[#E6E8EB]">Throughput velocity (Requests / min)</h3>
            <p className="text-[11px] text-[#8B929C]">Total requests per minute across production Envoy proxies</p>
          </div>
          <span className="text-[11px] text-[#8B929C] font-mono">Sampling: 1-min buckets</span>
        </div>

        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={stats.requests_over_time} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="trafficPageGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#4C8DFF" stopOpacity={0.2} />
                  <stop offset="100%" stopColor="#4C8DFF" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="2 2" stroke="#252A31" vertical={false} />
              <XAxis dataKey="timestamp" stroke="#5C626C" tick={{ fontSize: 10, fill: '#8B929C', fontFamily: 'JetBrains Mono' }} tickLine={false} />
              <YAxis stroke="#5C626C" tick={{ fontSize: 10, fill: '#8B929C', fontFamily: 'JetBrains Mono' }} tickLine={false} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-[#15181D] border border-[#252A31] p-2 rounded-[4px] text-[11px] font-mono text-[#E6E8EB]">
                        <div>Time: {payload[0].payload.timestamp}</div>
                        <div className="text-[#4C8DFF]">Volume: {payload[0].value} req/min</div>
                        <div className="text-[#E5484D]">Error rate: {payload[0].payload.error_rate}%</div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area type="monotone" dataKey="requests_per_min" stroke="#4C8DFF" strokeWidth={1.5} fill="url(#trafficPageGrad)" dot={false} isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Consumers & Status Code Mix */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Top consumers table */}
        <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] overflow-hidden">
          <div className="px-4 py-2.5 border-b border-[#252A31] bg-[#15181D] flex items-center justify-between">
            <h3 className="text-[13px] font-semibold text-[#E6E8EB]">Top consumers by request volume</h3>
            <span className="text-[11px] text-[#8B929C] font-mono">{stats.top_consumers.length} actors</span>
          </div>

          <table className="w-full text-left text-[12px] border-collapse font-mono">
            <thead className="bg-[#0E1013] text-[#8B929C] border-b border-[#252A31] text-[11px] select-none font-sans">
              <tr className="h-8">
                <th className="px-3 font-normal">Actor identifier</th>
                <th className="px-3 font-normal w-28 text-right">Requests</th>
                <th className="px-3 font-normal w-28 text-right">Error rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#252A31]">
              {stats.top_consumers.map((c, i) => (
                <tr key={i} className="h-9 hover:bg-[#1C2026] transition-colors">
                  <td className="px-3 text-[#E6E8EB]">{c.actor}</td>
                  <td className="px-3 text-right text-[#8B929C]">{c.requests.toLocaleString()}</td>
                  <td className="px-3 text-right">
                    <span className={c.error_rate > 30 ? 'text-[#E5484D] font-medium' : 'text-[#8B929C]'}>
                      {c.error_rate}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Status code breakdown */}
        <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-[13px] font-semibold text-[#E6E8EB]">HTTP response code distribution</h3>
              <span className="text-[11px] text-[#8B929C] font-mono">Gateway aggregated</span>
            </div>

            <div className="space-y-3 font-mono text-[12px]">
              {stats.status_codes.map((sc, i) => {
                const codeColor =
                  sc.code.startsWith('2') ? 'text-[#10b981]' :
                  sc.code.startsWith('4') ? 'text-[#E5484D]' : 'text-[#E5A100]';
                const barColor =
                  sc.code.startsWith('2') ? 'bg-[#10b981]' :
                  sc.code.startsWith('4') ? 'bg-[#E5484D]' : 'bg-[#E5A100]';

                return (
                  <div key={i} className="space-y-1">
                    <div className="flex justify-between items-center text-[11px]">
                      <span className={`font-semibold ${codeColor}`}>{sc.code}</span>
                      <span className="text-[#8B929C]">{sc.count.toLocaleString()} reqs ({sc.percentage}%)</span>
                    </div>
                    <div className="h-1.5 w-full bg-[#0E1013] rounded-full overflow-hidden">
                      <div
                        className={`h-full ${barColor}`}
                        style={{ width: `${sc.percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="pt-2 mt-4 border-t border-[#252A31] text-[11px] text-[#8B929C] flex items-center justify-between font-sans">
            <span>High 401/403 volume indicates credential spray</span>
            <span className="font-mono">Window: {window}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
