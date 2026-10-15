import React, { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useInventoryQuery } from '../api/queries';
import { useDashboardMetrics } from '../api/metrics';
import { StatusTag } from '../components/common/StatusTag';
import { MethodTag } from '../components/common/MethodTag';
import { RelativeTime } from '../components/common/RelativeTime';
import { Search } from 'lucide-react';

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
    <div className="space-y-4">
      {/* Header and status counts */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-[15px] font-semibold text-[#E6E8EB]">API inventory</h1>
          <p className="text-[12px] text-[#8B929C] mt-0.5">
            Continuous passive discovery across wire traffic diffed against registered openapi.yaml
          </p>
        </div>

        {/* Status segment filter pills */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
          <button
            onClick={() => handleStatusFilterChange('all')}
            className={`px-2 py-1 rounded-[4px] border transition-colors ${
              statusFilter === 'all'
                ? 'bg-[#1C2026] text-[#E6E8EB] border-[#343B45] font-medium'
                : 'bg-[#0E1013] text-[#8B929C] border-[#252A31] hover:text-[#E6E8EB]'
            }`}
          >
            All <span className="font-mono ml-1">{totalApis}</span>
          </button>
          <button
            onClick={() => handleStatusFilterChange('documented')}
            className={`px-2 py-1 rounded-[4px] border transition-colors ${
              statusFilter === 'documented'
                ? 'bg-[#1C2026] text-[#E6E8EB] border-[#343B45] font-medium'
                : 'bg-[#0E1013] text-[#8B929C] border-[#252A31] hover:text-[#E6E8EB]'
            }`}
          >
            Documented <span className="font-mono ml-1">{documentedCount}</span>
          </button>
          <button
            onClick={() => handleStatusFilterChange('shadow')}
            className={`px-2 py-1 rounded-[4px] border transition-colors ${
              statusFilter === 'shadow'
                ? 'bg-[#B47AEA]/20 text-[#B47AEA] border-[#B47AEA]/50 font-medium'
                : 'bg-[#0E1013] text-[#B47AEA] border-[#B47AEA]/30 hover:bg-[#B47AEA]/10'
            }`}
          >
            Shadow <span className="font-mono ml-1">{shadowCount}</span>
          </button>
          <button
            onClick={() => handleStatusFilterChange('zombie')}
            className={`px-2 py-1 rounded-[4px] border transition-colors ${
              statusFilter === 'zombie'
                ? 'bg-[#E5484D]/20 text-[#E5484D] border-[#E5484D]/50 font-medium'
                : 'bg-[#0E1013] text-[#E5484D] border-[#E5484D]/30 hover:bg-[#E5484D]/10'
            }`}
          >
            Zombie <span className="font-mono ml-1">{zombieCount}</span>
          </button>
          <button
            onClick={() => handleStatusFilterChange('unmanaged')}
            className={`px-2 py-1 rounded-[4px] border transition-colors ${
              statusFilter === 'unmanaged'
                ? 'bg-[#F76B15]/20 text-[#F76B15] border-[#F76B15]/50 font-medium'
                : 'bg-[#0E1013] text-[#F76B15] border-[#F76B15]/30 hover:bg-[#F76B15]/10'
            }`}
          >
            Unmanaged <span className="font-mono ml-1">{unmanagedCount}</span>
          </button>
          <button
            onClick={() => handleStatusFilterChange('unused_documented')}
            className={`px-2 py-1 rounded-[4px] border transition-colors ${
              statusFilter === 'unused_documented'
                ? 'bg-[#1C2026] text-[#8B929C] border-[#343B45] font-medium'
                : 'bg-[#0E1013] text-[#8B929C] border-[#252A31] hover:text-[#E6E8EB]'
            }`}
          >
            Unused <span className="font-mono ml-1">{unusedCount}</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-3 flex flex-col md:flex-row items-center justify-between gap-3 text-[12px]">
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-2.5 w-3.5 h-3.5 text-[#8B929C]" strokeWidth={1.5} />
          <input
            type="text"
            placeholder="Filter by path, parameter, sensitive field..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#0E1013] border border-[#252A31] focus:border-[#4C8DFF] rounded-[4px] pl-9 pr-3 py-1.5 text-[12px] text-[#E6E8EB] placeholder-[#8B929C] outline-hidden"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Auth filter */}
          <div className="flex items-center gap-1.5 text-[12px] text-[#8B929C]">
            <span>Auth:</span>
            <select
              value={authFilter}
              onChange={(e) => setAuthFilter(e.target.value)}
              className="bg-[#0E1013] border border-[#252A31] text-[#E6E8EB] rounded-[4px] px-2 py-1 text-[11px] outline-hidden"
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
          <div className="flex items-center gap-1.5 text-[12px] text-[#8B929C]">
            <span>Sensitive:</span>
            <select
              value={sensitiveFilter}
              onChange={(e) => setSensitiveFilter(e.target.value)}
              className="bg-[#0E1013] border border-[#252A31] text-[#E6E8EB] rounded-[4px] px-2 py-1 text-[11px] outline-hidden"
            >
              <option value="all">All data types</option>
              <option value="PAN">PAN</option>
              <option value="Aadhaar">Aadhaar</option>
              <option value="email">Email</option>
              <option value="phone">Phone</option>
            </select>
          </div>

          {/* Sort selector */}
          <div className="flex items-center gap-1.5 text-[12px] text-[#8B929C]">
            <span>Sort:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-[#0E1013] border border-[#252A31] text-[#E6E8EB] rounded-[4px] px-2 py-1 text-[11px] outline-hidden"
            >
              <option value="risk_desc">Highest risk first</option>
              <option value="risk_asc">Lowest risk first</option>
              <option value="requests_desc">Most requests</option>
            </select>
          </div>
        </div>
      </div>

      {/* Dense Inventory Table */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-[12px] border-collapse">
            <thead className="bg-[#0E1013] text-[#8B929C] sticky top-0 border-b border-[#252A31] text-[11px] select-none">
              <tr className="h-8">
                <th className="px-3 font-normal w-16">Method</th>
                <th className="px-3 font-normal">Path template</th>
                <th className="px-3 font-normal w-28">Status</th>
                <th className="px-3 font-normal w-24">Risk score</th>
                <th className="px-3 font-normal w-20">Auth</th>
                <th className="px-3 font-normal">Sensitive types</th>
                <th className="px-3 font-normal w-24 text-right">Requests</th>
                <th className="px-3 font-normal w-20 text-right">Last seen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#252A31]">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-[#8B929C]">
                    Loading inventory...
                  </td>
                </tr>
              ) : inventory.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-[#8B929C]">
                    No endpoints match the selected filters.
                  </td>
                </tr>
              ) : (
                inventory.map((item) => {
                  const riskColor =
                    item.risk_score >= 90 ? 'text-[#E5484D]' :
                    item.risk_score >= 75 ? 'text-[#F76B15]' :
                    item.risk_score >= 50 ? 'text-[#E5A100]' : 'text-[#8B929C]';

                  return (
                    <tr
                      key={item.api_id}
                      className="h-9 hover:bg-[#1C2026] cursor-pointer transition-colors"
                    >
                      {/* Method */}
                      <td className="px-3 whitespace-nowrap">
                        <Link to={`/inventory/${item.api_id}`} className="block">
                          <MethodTag method={item.method} />
                        </Link>
                      </td>

                      {/* Path */}
                      <td className="px-3 font-mono text-[12px] text-[#E6E8EB] max-w-sm truncate">
                        <Link to={`/inventory/${item.api_id}`} className="hover:text-[#4C8DFF] transition-colors">
                          {item.path_template}
                        </Link>
                      </td>

                      {/* Status */}
                      <td className="px-3 whitespace-nowrap">
                        <Link to={`/inventory/${item.api_id}`} className="block">
                          <StatusTag status={item.status} />
                        </Link>
                      </td>

                      {/* Risk score */}
                      <td className="px-3 whitespace-nowrap">
                        <Link to={`/inventory/${item.api_id}`} className="flex items-center gap-2">
                          <span className={`font-mono text-[12px] font-medium ${riskColor}`}>
                            {item.risk_score}
                          </span>
                          <div className="w-12 h-1 bg-[#0E1013] rounded-full overflow-hidden">
                            <div
                              className={`h-full ${
                                item.risk_score >= 90 ? 'bg-[#E5484D]' :
                                item.risk_score >= 75 ? 'bg-[#F76B15]' :
                                item.risk_score >= 50 ? 'bg-[#E5A100]' : 'bg-[#8B929C]'
                              }`}
                              style={{ width: `${item.risk_score}%` }}
                            />
                          </div>
                        </Link>
                      </td>

                      {/* Auth */}
                      <td className="px-3 text-[11px] text-[#8B929C] capitalize whitespace-nowrap">
                        <Link to={`/inventory/${item.api_id}`} className="block">
                          {item.auth_type}
                        </Link>
                      </td>

                      {/* Sensitive types */}
                      <td className="px-3">
                        <Link to={`/inventory/${item.api_id}`} className="flex flex-wrap gap-1">
                          {item.sensitive_types.length === 0 ? (
                            <span className="text-[11px] text-[#5C626C]">—</span>
                          ) : (
                            item.sensitive_types.map(s => (
                              <span
                                key={s}
                                className="px-1.5 py-0.2 rounded-[3px] bg-[#0E1013] border border-[#252A31] text-[10px] text-[#8B929C] font-mono"
                              >
                                {s}
                              </span>
                            ))
                          )}
                        </Link>
                      </td>

                      {/* Requests */}
                      <td className="px-3 text-right font-mono text-[12px] text-[#8B929C] whitespace-nowrap">
                        <Link to={`/inventory/${item.api_id}`} className="block">
                          {item.request_count.toLocaleString()}
                        </Link>
                      </td>

                      {/* Last seen */}
                      <td className="px-3 text-right whitespace-nowrap">
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
        <div className="px-4 py-2 border-t border-[#252A31] bg-[#0E1013] text-[11px] text-[#8B929C] flex items-center justify-between">
          <span>Showing {inventory.length} of {totalApis} endpoints</span>
          <span className="font-mono">openapi.yaml synchronization active</span>
        </div>
      </div>
    </div>
  );
};
