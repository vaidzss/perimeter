import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAlertsQuery } from '../api/queries';
import { useDashboardMetrics } from '../api/metrics';
import { SeverityDot } from '../components/common/SeverityDot';
import { RelativeTime } from '../components/common/RelativeTime';
import { Search, ShieldAlert, ArrowRight } from 'lucide-react';

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

  const filtered = alerts.filter((a) => {
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
        setSelectedIdx((prev) => Math.min(prev + 1, Math.max(0, filtered.length - 1)));
      } else if (e.key === 'k') {
        setSelectedIdx((prev) => Math.max(prev - 1, 0));
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
    <div className="space-y-5 select-none font-sans pb-12">
      {/* Header and summary strip */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-blue-600" />
            <h1 className="text-lg font-bold text-slate-900 tracking-tight">Security Threat Alerts</h1>
          </div>
          <p className="text-[12px] text-slate-500 mt-0.5">
            Continuous anomaly detection across BOLA, token misuse, scraping, brute force, and unauthorized access
          </p>
        </div>

        {/* Severity counts filter pills */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <button
            onClick={() => setSeverityFilter('all')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              severityFilter === 'all'
                ? 'bg-slate-900 text-white border-slate-900 font-semibold shadow-2xs'
                : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
            }`}
          >
            All <span className="font-mono ml-1">{totalAlerts}</span>
          </button>
          <button
            onClick={() => setSeverityFilter('critical')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              severityFilter === 'critical'
                ? 'bg-red-600 text-white border-red-600 font-semibold shadow-2xs'
                : 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100'
            }`}
          >
            Critical <span className="font-mono ml-1">{criticalAlerts}</span>
          </button>
          <button
            onClick={() => setSeverityFilter('high')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              severityFilter === 'high'
                ? 'bg-amber-600 text-white border-amber-600 font-semibold shadow-2xs'
                : 'bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100'
            }`}
          >
            High <span className="font-mono ml-1">{highAlerts}</span>
          </button>
          <button
            onClick={() => setSeverityFilter('medium')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              severityFilter === 'medium'
                ? 'bg-yellow-600 text-white border-yellow-600 font-semibold shadow-2xs'
                : 'bg-yellow-50 text-yellow-800 border-yellow-200 hover:bg-yellow-100'
            }`}
          >
            Medium <span className="font-mono ml-1">{mediumAlerts}</span>
          </button>
          <button
            onClick={() => setSeverityFilter('low')}
            className={`px-3 py-1.5 rounded-xl border transition-all ${
              severityFilter === 'low'
                ? 'bg-slate-700 text-white border-slate-700 font-semibold shadow-2xs'
                : 'bg-slate-100 text-slate-700 border-slate-200 hover:bg-slate-200'
            }`}
          >
            Low <span className="font-mono ml-1">{lowAlerts}</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 flex flex-col md:flex-row items-center justify-between gap-3 text-xs shadow-xs">
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" strokeWidth={2} />
          <input
            type="text"
            placeholder="Search alerts by API, actor, ID, reason..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 focus:border-blue-600 rounded-xl pl-10 pr-3.5 py-2 text-xs text-slate-900 placeholder-slate-400 outline-none transition-colors"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Attack type filter */}
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <span>Type:</span>
            <select
              value={typeFilter}
              onChange={(e) => handleTypeChange(e.target.value)}
              className="bg-slate-50 border border-slate-200 text-slate-800 rounded-xl px-3 py-1.5 text-xs outline-none cursor-pointer"
            >
              <option value="all">All threat types</option>
              <option value="BOLA">BOLA</option>
              <option value="token_misuse">Token misuse</option>
              <option value="scraping">Scraping</option>
              <option value="brute_force">Brute force</option>
              <option value="unauthorized_access">Unauthorized access</option>
            </select>
          </div>

          {/* Status filter */}
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <span>Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-50 border border-slate-200 text-slate-800 rounded-xl px-3 py-1.5 text-xs outline-none cursor-pointer"
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
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-slate-50 text-slate-500 sticky top-0 border-b border-slate-200 text-[11px] select-none">
              <tr className="h-9">
                <th className="px-4 font-semibold w-24">Severity</th>
                <th className="px-4 font-semibold w-24">ID</th>
                <th className="px-4 font-semibold">Reason / Indicator</th>
                <th className="px-4 font-semibold">Endpoint</th>
                <th className="px-4 font-semibold w-20">Actor</th>
                <th className="px-4 font-semibold w-24">OWASP</th>
                <th className="px-4 font-semibold w-24">Last seen</th>
                <th className="px-4 font-semibold w-24 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center text-slate-400 font-mono">
                    Loading alerts...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center text-slate-500 font-mono">
                    No security alerts match the specified filter criteria.
                  </td>
                </tr>
              ) : (
                filtered.map((alert, idx) => {
                  const isSelected = idx === selectedIdx;
                  const isCritical = alert.severity === 'critical';

                  return (
                    <tr
                      key={alert.alert_id}
                      onClick={() => navigate(`/alerts/${alert.alert_id}`)}
                      onMouseEnter={() => setSelectedIdx(idx)}
                      className={`h-11 cursor-pointer transition-colors ${
                        isSelected ? 'bg-blue-50/70 border-l-2 border-l-blue-600' : 'hover:bg-slate-50'
                      }`}
                    >
                      {/* Severity */}
                      <td className="px-4 whitespace-nowrap">
                        <SeverityDot severity={alert.severity} />
                      </td>

                      {/* Alert ID */}
                      <td className="px-4 font-mono text-[11px] text-slate-500 whitespace-nowrap font-medium">
                        {alert.alert_id}
                      </td>

                      {/* Reason */}
                      <td className="px-4 text-slate-900 font-medium max-w-md truncate" title={alert.reason}>
                        {alert.reason}
                      </td>

                      {/* Endpoint (mono) */}
                      <td className="px-4 font-mono text-xs text-slate-600 truncate max-w-[200px]">
                        {alert.api}
                      </td>

                      {/* Actor (mono) */}
                      <td className="px-4 font-mono text-xs text-slate-700 whitespace-nowrap font-semibold">
                        {alert.actor}
                      </td>

                      {/* OWASP */}
                      <td className="px-4 text-[11px] text-slate-500 whitespace-nowrap font-mono">
                        {alert.owasp.split(' ')[0]}
                      </td>

                      {/* Age */}
                      <td className="px-4 whitespace-nowrap text-slate-500 font-mono text-[11px]">
                        <RelativeTime timestamp={alert.last_seen} />
                      </td>

                      {/* Status */}
                      <td className="px-4 text-right whitespace-nowrap">
                        <span
                          className={`text-[11px] px-2 py-0.5 rounded-full font-semibold border ${
                            alert.status === 'open'
                              ? 'text-red-700 border-red-200 bg-red-50'
                              : alert.status === 'investigating'
                              ? 'text-amber-800 border-amber-200 bg-amber-50'
                              : 'text-emerald-800 border-emerald-200 bg-emerald-50'
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
        <div className="px-5 py-3 border-t border-slate-200 bg-slate-50 text-xs text-slate-500 flex items-center justify-between font-mono">
          <span>Showing {filtered.length} of {totalAlerts} alerts</span>
          <span>Use <kbd className="px-1.5 py-0.5 rounded bg-white border border-slate-200 shadow-2xs">j</kbd>/<kbd className="px-1.5 py-0.5 rounded bg-white border border-slate-200 shadow-2xs">k</kbd> to move, <kbd className="px-1.5 py-0.5 rounded bg-white border border-slate-200 shadow-2xs">↵</kbd> to view forensic evidence</span>
        </div>
      </div>
    </div>
  );
};

export default AlertsPage;
