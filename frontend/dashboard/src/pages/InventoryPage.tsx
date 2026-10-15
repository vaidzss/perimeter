import React, { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useInventoryQuery } from '../api/queries';
import { useDashboardMetrics } from '../api/metrics';
import { StatusTag } from '../components/common/StatusTag';
import { MethodTag } from '../components/common/MethodTag';
import { RelativeTime } from '../components/common/RelativeTime';
import { Search, Database, Layers } from 'lucide-react';

export const InventoryPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialStatus = searchParams.get('status') || 'all';

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState(initialStatus);
  const [authFilter, setAuthFilter] = useState('all');
  const [sensitiveFilter, setSensitiveFilter] = useState('all');
  const [sortBy, setSortBy] = useState('risk_desc');

  const {
    totalApis,
    documentedCount,
    shadowCount,
    zombieCount,
    unmanagedCount,
    unusedCount,
  } = useDashboardMetrics();

  const { data: inventory = [], isLoading } = useInventoryQuery({
    status: statusFilter,
    auth: authFilter,
    sensitive: sensitiveFilter,
    q: searchTerm,
    sort: sortBy,
  });

  const handleStatusFilterChange = (status: string) => {
    setStatusFilter(status);
    if (status === 'all') {
      searchParams.delete('status');
    } else {
      searchParams.set('status', status);
    }
    setSearchParams(searchParams);
  };

  return (
    <div className="space-y-5 select-none font-sans pb-12">
      {/* Header and status counts */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-600" />
            <h1 className="text-lg font-bold text-slate-900 tracking-tight">API Inventory & Catalog</h1>
          </div>
          <p className="text-[12px] text-slate-500 mt-0.5">
            Continuous passive discovery across wire traffic diffed against registered openapi.yaml
          </p>
        </div>

        {/* Status segment filter pills */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <button
            onClick={() => handleStatusFilterChange('all')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              statusFilter === 'all'
                ? 'bg-slate-900 text-white border-slate-900 font-semibold shadow-2xs'
                : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
            }`}
          >
            All <span className="font-mono ml-1">{totalApis}</span>
          </button>
          <button
            onClick={() => handleStatusFilterChange('documented')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              statusFilter === 'documented'
                ? 'bg-emerald-600 text-white border-emerald-600 font-semibold shadow-2xs'
                : 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100'
            }`}
          >
            Documented <span className="font-mono ml-1">{documentedCount}</span>
          </button>
          <button
            onClick={() => handleStatusFilterChange('shadow')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              statusFilter === 'shadow'
                ? 'bg-amber-600 text-white border-amber-600 font-semibold shadow-2xs'
                : 'bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100'
            }`}
          >
            Shadow <span className="font-mono ml-1">{shadowCount}</span>
          </button>
          <button
            onClick={() => handleStatusFilterChange('zombie')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              statusFilter === 'zombie'
                ? 'bg-rose-600 text-white border-rose-600 font-semibold shadow-2xs'
                : 'bg-rose-50 text-rose-800 border-rose-200 hover:bg-rose-100'
            }`}
          >
            Zombie <span className="font-mono ml-1">{zombieCount}</span>
          </button>
          <button
            onClick={() => handleStatusFilterChange('unmanaged')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              statusFilter === 'unmanaged'
                ? 'bg-sky-600 text-white border-sky-600 font-semibold shadow-2xs'
                : 'bg-sky-50 text-sky-800 border-sky-200 hover:bg-sky-100'
            }`}
          >
            Unmanaged <span className="font-mono ml-1">{unmanagedCount}</span>
          </button>
          <button
            onClick={() => handleStatusFilterChange('unused_documented')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              statusFilter === 'unused_documented'
                ? 'bg-slate-700 text-white border-slate-700 font-semibold shadow-2xs'
                : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
            }`}
          >
            Unused <span className="font-mono ml-1">{unusedCount}</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 flex flex-col md:flex-row items-center justify-between gap-3 text-xs shadow-xs">
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" strokeWidth={2} />
          <input
            type="text"
            placeholder="Filter by path, parameter, sensitive field..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 focus:border-blue-600 rounded-xl pl-10 pr-3.5 py-2 text-xs text-slate-900 placeholder-slate-400 outline-none transition-colors"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Auth filter */}
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <span>Auth:</span>
            <select
              value={authFilter}
              onChange={(e) => setAuthFilter(e.target.value)}
              className="bg-slate-50 border border-slate-200 text-slate-800 rounded-xl px-3 py-1.5 text-xs outline-none cursor-pointer"
            >
              <option value="all">All auth</option>
              <option value="jwt">JWT</option>
              <option value="oauth2">OAuth2</option>
              <option value="api_key">API key</option>
              <option value="basic">Basic</option>
              <option value="none">None</option>
            </select>
          </div>

          {/* Sensitive data filter */}
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <span>Sensitive:</span>
            <select
              value={sensitiveFilter}
              onChange={(e) => setSensitiveFilter(e.target.value)}
              className="bg-slate-50 border border-slate-200 text-slate-800 rounded-xl px-3 py-1.5 text-xs outline-none cursor-pointer"
            >
              <option value="all">All data types</option>
              <option value="PAN">PAN</option>
              <option value="Aadhaar">Aadhaar</option>
              <option value="email">Email</option>
              <option value="phone">Phone</option>
            </select>
          </div>

          {/* Sort selector */}
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <span>Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-slate-50 border border-slate-200 text-slate-800 rounded-xl px-3 py-1.5 text-xs outline-none cursor-pointer"
            >
              <option value="risk_desc">Highest risk first</option>
              <option value="risk_asc">Lowest risk first</option>
              <option value="requests_desc">Most requests</option>
            </select>
          </div>
        </div>
      </div>

      {/* Dense Inventory Table */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-50 text-slate-500 sticky top-0 border-b border-slate-200 text-[11px] select-none font-sans">
              <tr className="h-9">
                <th className="px-4 font-semibold w-16">Method</th>
                <th className="px-4 font-semibold">Path Template</th>
                <th className="px-4 font-semibold w-28">Status</th>
                <th className="px-4 font-semibold w-28">Risk Score</th>
                <th className="px-4 font-semibold w-20">Auth</th>
                <th className="px-4 font-semibold">Sensitive Types</th>
                <th className="px-4 font-semibold w-24 text-right">Requests</th>
                <th className="px-4 font-semibold w-24 text-right">Last Seen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center text-slate-400 font-mono">
                    Loading inventory...
                  </td>
                </tr>
              ) : inventory.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center text-slate-500 font-mono">
                    No endpoints match the selected filters.
                  </td>
                </tr>
              ) : (
                inventory.map((item) => {
                  const riskColor =
                    item.risk_score >= 90 ? 'text-red-700' :
                    item.risk_score >= 75 ? 'text-amber-800' :
                    item.risk_score >= 50 ? 'text-yellow-800' : 'text-slate-600';

                  return (
                    <tr
                      key={item.api_id}
                      className="h-11 hover:bg-slate-50 cursor-pointer transition-colors"
                    >
                      {/* Method */}
                      <td className="px-4 whitespace-nowrap">
                        <Link to={`/inventory/${item.api_id}`} className="block">
                          <MethodTag method={item.method} />
                        </Link>
                      </td>

                      {/* Path */}
                      <td className="px-4 font-mono text-xs text-slate-900 max-w-sm truncate font-semibold">
                        <Link to={`/inventory/${item.api_id}`} className="hover:text-blue-600 transition-colors">
                          {item.path_template}
                        </Link>
                      </td>

                      {/* Status */}
                      <td className="px-4 whitespace-nowrap">
                        <Link to={`/inventory/${item.api_id}`} className="block">
                          <StatusTag status={item.status} />
                        </Link>
                      </td>

                      {/* Risk score */}
                      <td className="px-4 whitespace-nowrap">
                        <Link to={`/inventory/${item.api_id}`} className="flex items-center gap-2">
                          <span className={`font-mono text-xs font-bold ${riskColor}`}>
                            {item.risk_score}
                          </span>
                          <div className="w-14 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                item.risk_score >= 90 ? 'bg-red-600' :
                                item.risk_score >= 75 ? 'bg-amber-500' :
                                item.risk_score >= 50 ? 'bg-yellow-400' : 'bg-slate-400'
                              }`}
                              style={{ width: `${item.risk_score}%` }}
                            />
                          </div>
                        </Link>
                      </td>

                      {/* Auth */}
                      <td className="px-4 text-[11px] text-slate-600 capitalize whitespace-nowrap font-medium">
                        <Link to={`/inventory/${item.api_id}`} className="block">
                          {item.auth_type}
                        </Link>
                      </td>

                      {/* Sensitive types */}
                      <td className="px-4">
                        <Link to={`/inventory/${item.api_id}`} className="flex flex-wrap gap-1">
                          {item.sensitive_types.length === 0 ? (
                            <span className="text-xs text-slate-400">—</span>
                          ) : (
                            item.sensitive_types.map((s) => (
                              <span
                                key={s}
                                className="px-2 py-0.5 rounded-md bg-slate-100 border border-slate-200 text-[10.5px] text-slate-700 font-mono font-medium shadow-2xs"
                              >
                                {s}
                              </span>
                            ))
                          )}
                        </Link>
                      </td>

                      {/* Requests */}
                      <td className="px-4 text-right font-mono text-xs text-slate-600 whitespace-nowrap">
                        <Link to={`/inventory/${item.api_id}`} className="block">
                          {item.request_count.toLocaleString()}
                        </Link>
                      </td>

                      {/* Last seen */}
                      <td className="px-4 text-right whitespace-nowrap font-mono text-[11px] text-slate-500">
                        <Link to={`/inventory/${item.api_id}`} className="block">
                          <RelativeTime timestamp={item.last_seen} />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Table footer */}
        <div className="px-5 py-3 border-t border-slate-200 bg-slate-50 text-xs text-slate-500 flex items-center justify-between font-mono">
          <span>Showing {inventory.length} of {totalApis} endpoints</span>
          <span className="text-blue-600 font-semibold">openapi.yaml synchronization active</span>
        </div>
      </div>
    </div>
  );
};

export default InventoryPage;
