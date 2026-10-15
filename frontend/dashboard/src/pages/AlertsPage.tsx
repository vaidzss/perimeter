import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAlertsQuery } from '../api/queries';
import { useDashboardMetrics } from '../api/metrics';
import { SeverityDot } from '../components/common/SeverityDot';
import { RelativeTime } from '../components/common/RelativeTime';
import { Search } from 'lucide-react';

export const AlertsPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const initialType = searchParams.get('type') || 'all';

  const [severityFilter, setSeverityFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState(initialType);
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIdx, setSelectedIdx] = useState(0);

  const {
    totalAlerts,
    criticalAlerts,
    highAlerts,
    mediumAlerts,
    lowAlerts,
  } = useDashboardMetrics();

  const { data: alerts = [], isLoading } = useAlertsQuery({
    severity: severityFilter,
    type: typeFilter,
    status: statusFilter,
  });

  const filtered = alerts.filter(a => {
    if (!searchTerm) return true;
    const s = searchTerm.toLowerCase();
    return (
      a.reason.toLowerCase().includes(s) ||
      a.api.toLowerCase().includes(s) ||
      a.actor.toLowerCase().includes(s) ||
      a.alert_id.toLowerCase().includes(s) ||
      a.owasp.toLowerCase().includes(s)
    );
  });

  // Keyboard navigation (j/k to select, Enter to open)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (document.activeElement?.tagName === 'INPUT') return;
      if (e.key === 'j') {
        setSelectedIdx(prev => Math.min(prev + 1, Math.max(0, filtered.length - 1)));
      } else if (e.key === 'k') {
        setSelectedIdx(prev => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter') {
        if (filtered[selectedIdx]) {
          navigate(`/alerts/${filtered[selectedIdx].alert_id}`);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [filtered, selectedIdx, navigate]);

  const handleTypeChange = (val: string) => {
    setTypeFilter(val);
    if (val === 'all') {
      searchParams.delete('type');
    } else {
      searchParams.set('type', val);
    }
    setSearchParams(searchParams);
  };

  return (
    <div className="space-y-4">
      {/* Header and summary strip */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-[15px] font-semibold text-[#E6E8EB]">Security threat alerts</h1>
          <p className="text-[12px] text-[#8B929C] mt-0.5">
            Continuous anomaly detection across BOLA, token misuse, scraping, brute force, and unauthorized access
          </p>
        </div>

        {/* Severity counts filter pills */}
        <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
          <button
            onClick={() => setSeverityFilter('all')}
            className={`px-2 py-1 rounded-[4px] border transition-colors ${
              severityFilter === 'all'
                ? 'bg-[#1C2026] text-[#E6E8EB] border-[#343B45] font-medium'
                : 'bg-[#0E1013] text-[#8B929C] border-[#252A31] hover:text-[#E6E8EB]'
            }`}
          >
            All <span className="font-mono ml-1">{totalAlerts}</span>
          </button>
          <button
            onClick={() => setSeverityFilter('critical')}
            className={`px-2 py-1 rounded-[4px] border transition-colors ${
              severityFilter === 'critical'
                ? 'bg-[#E5484D]/20 text-[#E5484D] border-[#E5484D]/50 font-medium'
                : 'bg-[#0E1013] text-[#E5484D] border-[#E5484D]/30 hover:bg-[#E5484D]/10'
            }`}
          >
            Critical <span className="font-mono ml-1">{criticalAlerts}</span>
          </button>
          <button
            onClick={() => setSeverityFilter('high')}
            className={`px-2 py-1 rounded-[4px] border transition-colors ${
              severityFilter === 'high'
                ? 'bg-[#F76B15]/20 text-[#F76B15] border-[#F76B15]/50 font-medium'
                : 'bg-[#0E1013] text-[#F76B15] border-[#F76B15]/30 hover:bg-[#F76B15]/10'
            }`}
          >
            High <span className="font-mono ml-1">{highAlerts}</span>
          </button>
          <button
            onClick={() => setSeverityFilter('medium')}
            className={`px-2 py-1 rounded-[4px] border transition-colors ${
              severityFilter === 'medium'
                ? 'bg-[#E5A100]/20 text-[#E5A100] border-[#E5A100]/50 font-medium'
                : 'bg-[#0E1013] text-[#E5A100] border-[#E5A100]/30 hover:bg-[#E5A100]/10'
            }`}
          >
            Medium <span className="font-mono ml-1">{mediumAlerts}</span>
          </button>
          <button
            onClick={() => setSeverityFilter('low')}
            className={`px-2 py-1 rounded-[4px] border transition-colors ${
              severityFilter === 'low'
                ? 'bg-[#1C2026] text-[#8B929C] border-[#343B45] font-medium'
                : 'bg-[#0E1013] text-[#8B929C] border-[#252A31] hover:text-[#E6E8EB]'
            }`}
          >
            Low <span className="font-mono ml-1">{lowAlerts}</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-3 flex flex-col md:flex-row items-center justify-between gap-3 text-[12px]">
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3 top-2.5 w-3.5 h-3.5 text-[#8B929C]" strokeWidth={1.5} />
          <input
            type="text"
            placeholder="Search alerts by API, actor, ID, reason..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#0E1013] border border-[#252A31] focus:border-[#4C8DFF] rounded-[4px] pl-9 pr-3 py-1.5 text-[12px] text-[#E6E8EB] placeholder-[#8B929C] outline-hidden"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Attack type filter */}
          <div className="flex items-center gap-1.5 text-[12px] text-[#8B929C]">
            <span>Type:</span>
            <select
              value={typeFilter}
              onChange={(e) => handleTypeChange(e.target.value)}
              className="bg-[#0E1013] border border-[#252A31] text-[#E6E8EB] rounded-[4px] px-2 py-1 text-[11px] outline-hidden"
            >
              <option value="all">All types</option>
              <option value="BOLA">BOLA</option>
              <option value="token_misuse">Token misuse</option>
              <option value="scraping">Scraping</option>
              <option value="brute_force">Brute force</option>
              <option value="unauthorized_access">Unauthorized access</option>
            </select>
          </div>

          {/* Status filter */}
          <div className="flex items-center gap-1.5 text-[12px] text-[#8B929C]">
            <span>Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-[#0E1013] border border-[#252A31] text-[#E6E8EB] rounded-[4px] px-2 py-1 text-[11px] outline-hidden"
            >
              <option value="all">All statuses</option>
              <option value="open">Open</option>
              <option value="investigating">Investigating</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </div>
      </div>

      {/* Dense Alerts Table */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-[12px] border-collapse">
            <thead className="bg-[#0E1013] text-[#8B929C] sticky top-0 border-b border-[#252A31] text-[11px] select-none">
              <tr className="h-8">
                <th className="px-3 font-normal w-24">Severity</th>
                <th className="px-3 font-normal w-24">ID</th>
                <th className="px-3 font-normal">Reason / Indicator</th>
                <th className="px-3 font-normal">Endpoint</th>
                <th className="px-3 font-normal w-20">Actor</th>
                <th className="px-3 font-normal w-24">OWASP</th>
                <th className="px-3 font-normal w-20">Last seen</th>
                <th className="px-3 font-normal w-24 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#252A31]">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-[#8B929C]">
                    Loading alerts...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-[#8B929C]">
                    No security alerts match the specified filter criteria.
                  </td>
                </tr>
              ) : (
                filtered.map((alert, idx) => {
                  const isSelected = idx === selectedIdx;
                  const isCritical = alert.severity === 'critical';
                  const isTopCritical = idx === 0 && isCritical;

                  return (
                    <tr
                      key={alert.alert_id}
                      onClick={() => navigate(`/alerts/${alert.alert_id}`)}
                      onMouseEnter={() => setSelectedIdx(idx)}
                      className={`h-9 cursor-pointer transition-colors ${
                        isSelected ? 'bg-[#1C2026]' : 'hover:bg-[#1C2026]/60'
                      } ${isTopCritical ? 'border-l-2 border-l-[#E5484D]' : ''}`}
                    >
                      {/* Severity */}
                      <td className="px-3 whitespace-nowrap">
                        <SeverityDot severity={alert.severity} />
                      </td>

                      {/* Alert ID */}
                      <td className="px-3 font-mono text-[11px] text-[#8B929C] whitespace-nowrap">
                        {alert.alert_id}
                      </td>

                      {/* Reason */}
                      <td className="px-3 text-[#E6E8EB] max-w-md truncate" title={alert.reason}>
                        {alert.reason}
                      </td>

                      {/* Endpoint (mono) */}
                      <td className="px-3 font-mono text-[12px] text-[#8B929C] truncate max-w-[200px]">
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
                              : alert.status === 'investigating'
                              ? 'text-[#E5A100] border-[#E5A100]/30 bg-[#E5A100]/10'
                              : 'text-[#8B929C] border-[#252A31] bg-[#0E1013]'
                          }`}
                        >
                          {alert.status}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-[#252A31] bg-[#0E1013] text-[11px] text-[#8B929C] flex items-center justify-between">
          <span>Showing {filtered.length} of {totalAlerts} alerts</span>
          <span>Use <kbd className="font-mono px-1 py-0.2 rounded bg-[#15181D] border border-[#252A31]">j</kbd>/<kbd className="font-mono px-1 py-0.2 rounded bg-[#15181D] border border-[#252A31]">k</kbd> to move, <kbd className="font-mono px-1 py-0.2 rounded bg-[#15181D] border border-[#252A31]">↵</kbd> to view forensic evidence</span>
        </div>
      </div>
    </div>
  );
};
