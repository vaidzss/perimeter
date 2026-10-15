import React, { useState } from 'react';
import { useTrafficStatsQuery } from '../api/queries';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Activity, Clock, ShieldCheck, AlertTriangle } from 'lucide-react';

export const TrafficPage: React.FC = () => {
  const [window, setWindow] = useState('1h');
  const { data: stats, isLoading } = useTrafficStatsQuery(window);

  if (isLoading || !stats) {
    return (
      <div className="space-y-4 animate-pulse select-none">
        <div className="h-16 rounded-2xl bg-white border border-slate-200 shadow-xs" />
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-24 rounded-xl bg-white border border-slate-200 shadow-xs" />
          ))}
        </div>
        <div className="h-72 rounded-2xl bg-white border border-slate-200 shadow-xs" />
      </div>
    );
  }

  return (
    <div className="space-y-5 select-none font-sans pb-12">
      {/* Header and window picker */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            <h1 className="text-lg font-bold text-slate-900 tracking-tight">Traffic Telemetry & Baselines</h1>
          </div>
          <p className="text-[12px] text-slate-500 mt-0.5">
            Ingress gateway telemetry, latency percentiles, error rates, and top consumer attribution
          </p>
        </div>

        {/* Time window selector */}
        <div className="flex items-center gap-1 bg-slate-100 border border-slate-200 p-1 rounded-xl text-xs self-start md:self-center font-mono">
          {['15m', '1h', '6h', '24h'].map((w) => (
            <button
              key={w}
              onClick={() => setWindow(w)}
              className={`px-3 py-1 rounded-lg transition-all ${
                window === w
                  ? 'bg-white text-blue-700 font-semibold shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {w}
            </button>
          ))}
        </div>
      </div>

      {/* Latency & Error Rate Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs">
          <span className="text-xs text-slate-500 font-medium">p50 Median Latency</span>
          <div className="text-2xl font-bold text-slate-900 font-mono mt-1">
            {stats.latency_percentiles.p50} <span className="text-xs font-normal text-slate-500">ms</span>
          </div>
          <span className="text-[11px] text-emerald-700 font-medium font-mono">Baseline compliant</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs">
          <span className="text-xs text-slate-500 font-medium">p90 Latency</span>
          <div className="text-2xl font-bold text-slate-900 font-mono mt-1">
            {stats.latency_percentiles.p90} <span className="text-xs font-normal text-slate-500">ms</span>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">Nominal SLA</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs">
          <span className="text-xs text-slate-500 font-medium">p99 Latency</span>
          <div className="text-2xl font-bold text-slate-900 font-mono mt-1">
            {stats.latency_percentiles.p99} <span className="text-xs font-normal text-slate-500">ms</span>
          </div>
          <span className="text-[11px] text-slate-500 font-mono">Spike ceiling</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs">
          <span className="text-xs text-slate-500 font-medium">4xx Error Rate</span>
          <div className="text-2xl font-bold text-rose-600 font-mono mt-1">
            {stats.error_rates.rate_4xx}%
          </div>
          <span className="text-[11px] text-rose-700 font-medium font-mono">Client probes</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs">
          <span className="text-xs text-slate-500 font-medium">5xx Error Rate</span>
          <div className="text-2xl font-bold text-slate-900 font-mono mt-1">
            {stats.error_rates.rate_5xx}%
          </div>
          <span className="text-[11px] text-emerald-700 font-medium font-mono">0 crashes</span>
        </div>
      </div>

      {/* Requests over time chart */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col justify-between shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Throughput Velocity (Requests / min)</h3>
            <p className="text-xs text-slate-500 mt-0.5">Total requests per minute across production Envoy proxies</p>
          </div>
          <span className="text-xs text-slate-400 font-mono">Sampling: 1-min buckets</span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={stats.requests_over_time} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
              <defs>
                <linearGradient id="trafficPageGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#2563EB" stopOpacity={0.15} />
                  <stop offset="100%" stopColor="#2563EB" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
              <XAxis dataKey="timestamp" stroke="#E2E8F0" tick={{ fontSize: 10, fill: '#64748B', fontFamily: 'JetBrains Mono' }} tickLine={false} />
              <YAxis stroke="#E2E8F0" tick={{ fontSize: 10, fill: '#64748B', fontFamily: 'JetBrains Mono' }} tickLine={false} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-white border border-slate-200 p-3 rounded-xl text-xs font-mono text-slate-900 shadow-xl">
                        <div className="text-slate-400 text-[11px] mb-1">Time: {payload[0].payload.timestamp}</div>
                        <div className="text-blue-600 font-bold">Volume: {payload[0].value} req/min</div>
                        <div className="text-rose-600">Error rate: {payload[0].payload.error_rate}%</div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area type="monotone" dataKey="requests_per_min" stroke="#2563EB" strokeWidth={2} fill="url(#trafficPageGrad)" dot={false} isAnimationActive={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Consumers & Status Code Mix */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Top consumers table */}
        <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
          <div className="px-5 py-3.5 border-b border-slate-100 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-900">Top Consumers by Request Volume</h3>
            <span className="text-xs text-slate-400 font-mono">{stats.top_consumers.length} actors</span>
          </div>

          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead className="bg-slate-50 text-slate-500 border-b border-slate-200 text-[11px] select-none font-sans">
              <tr className="h-9">
                <th className="px-5 font-medium">Actor Identifier</th>
                <th className="px-5 font-medium w-28 text-right">Requests</th>
                <th className="px-5 font-medium w-28 text-right">Error Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {stats.top_consumers.map((c, i) => (
                <tr key={i} className="h-10 hover:bg-slate-50 transition-colors">
                  <td className="px-5 text-slate-800 font-semibold">{c.actor}</td>
                  <td className="px-5 text-right text-slate-600">{c.requests.toLocaleString()}</td>
                  <td className="px-5 text-right">
                    <span className={c.error_rate > 30 ? 'text-rose-600 font-bold' : 'text-slate-600'}>
                      {c.error_rate}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Status code breakdown */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col justify-between shadow-xs">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-slate-900">HTTP Response Code Distribution</h3>
              <span className="text-xs text-slate-400 font-mono">Gateway aggregated</span>
            </div>

            <div className="space-y-3 font-mono text-xs">
              {stats.status_codes.map((sc, i) => {
                const codeColor =
                  sc.code.startsWith('2') ? 'text-emerald-700' :
                  sc.code.startsWith('4') ? 'text-rose-700' : 'text-amber-700';
                const barColor =
                  sc.code.startsWith('2') ? 'bg-emerald-500' :
                  sc.code.startsWith('4') ? 'bg-rose-500' : 'bg-amber-500';

                return (
                  <div key={i} className="space-y-1">
                    <div className="flex justify-between items-center text-[11.5px]">
                      <span className={`font-bold ${codeColor}`}>{sc.code}</span>
                      <span className="text-slate-500">{sc.count.toLocaleString()} reqs ({sc.percentage}%)</span>
                    </div>
                    <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
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

          <div className="pt-3 mt-4 border-t border-slate-100 text-xs text-slate-500 flex items-center justify-between font-sans">
            <span>High 401/403 volume indicates credential spray</span>
            <span className="font-mono text-slate-400">Window: {window}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrafficPage;
