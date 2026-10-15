import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Database, ShieldAlert, Activity, FileText, X, ArrowRight, Sliders, Globe } from 'lucide-react';
import { useDashboardMetrics } from '../../api/metrics';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenDemoDrawer: () => void;
}

interface CommandItem {
  id: string;
  title: string;
  subtitle?: string;
  category: string;
  route?: string;
  action?: () => void;
  icon: React.ComponentType<{ className?: string; strokeWidth?: number }>;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose, onOpenDemoDrawer }) => {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const navigate = useNavigate();
  const { inventory, alerts } = useDashboardMetrics();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Build searchable items
  const staticItems: CommandItem[] = [
    { id: 'p-landing', title: 'Product Landing Page', subtitle: 'Showcase & Architectural Proofs', category: 'Pages', route: '/', icon: Globe },
    { id: 'p-overview', title: 'Security Posture & Telemetry', subtitle: 'Real-time scores & traffic radar', category: 'Pages', route: '/overview', icon: ShieldAlert },
    { id: 'p-inventory', title: 'API Inventory (All Endpoints)', subtitle: 'Passive discovery catalog', category: 'Pages', route: '/inventory', icon: Database },
    { id: 'p-shadow', title: 'Shadow APIs Filtered', subtitle: 'Undocumented and drifting routes', category: 'Pages', route: '/inventory?status=shadow', icon: Database },
    { id: 'p-alerts', title: 'Security Threat Alerts', subtitle: 'BOLA, token misuse, scraping', category: 'Pages', route: '/alerts', icon: ShieldAlert },
    { id: 'p-traffic', title: 'Traffic Telemetry & Baselines', subtitle: 'Ingress percentiles & error rates', category: 'Pages', route: '/traffic', icon: Activity },
    { id: 'p-eval', title: 'Detector Benchmark Evaluation', subtitle: 'Precision, recall & confusion matrix', category: 'Pages', route: '/evaluation', icon: FileText },
    { id: 'p-demo', title: 'Demo Controls Drawer (Shift+D)', subtitle: 'Trigger attack simulations', category: 'Actions', action: () => { onClose(); onOpenDemoDrawer(); }, icon: Sliders },
  ];

  const apiItems: CommandItem[] = (inventory || []).slice(0, 15).map(item => ({
    id: `api-${item.api_id}`,
    title: `${item.method} ${item.path_template}`,
    subtitle: item.status === 'shadow' ? 'Shadow API' : `${item.status} · ${item.sensitive_types.join(', ')}`,
    category: 'Endpoints',
    route: `/inventory/${item.api_id}`,
    icon: Database,
  }));

  const alertItems: CommandItem[] = (alerts || []).slice(0, 10).map(a => ({
    id: `alt-${a.alert_id}`,
    title: `${a.type}: ${a.api}`,
    subtitle: `${a.severity.toUpperCase()} · Actor: ${a.actor}`,
    category: 'Alerts',
    route: `/alerts/${a.alert_id}`,
    icon: ShieldAlert,
  }));

  const allItems: CommandItem[] = [...staticItems, ...apiItems, ...alertItems];

  const filtered = query.trim() === ''
    ? allItems.slice(0, 12)
    : allItems.filter(item =>
        item.title.toLowerCase().includes(query.toLowerCase()) ||
        item.category.toLowerCase().includes(query.toLowerCase()) ||
        (item.subtitle && item.subtitle.toLowerCase().includes(query.toLowerCase()))
      ).slice(0, 14);

  const handleSelect = (item: CommandItem) => {
    onClose();
    if (item.action) {
      item.action();
    } else if (item.route) {
      navigate(item.route);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-slate-900/35 backdrop-blur-xs p-4">
      <div className="w-full max-w-xl rounded-2xl bg-white border border-slate-200 shadow-2xl overflow-hidden flex flex-col text-slate-900 animate-in fade-in zoom-in-95 duration-150">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3 border-b border-slate-200 bg-slate-50/50 gap-2.5">
          <Search className="w-4 h-4 text-slate-400 shrink-0" strokeWidth={2} />
          <input
            type="text"
            autoFocus
            placeholder="Type a command, endpoint, or alert..."
            value={query}
            onChange={e => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={e => {
              if (e.key === 'ArrowDown') {
                e.preventDefault();
                setSelectedIndex(prev => (prev + 1) % Math.max(1, filtered.length));
              } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                setSelectedIndex(prev => (prev - 1 + filtered.length) % Math.max(1, filtered.length));
              } else if (e.key === 'Enter') {
                e.preventDefault();
                if (filtered[selectedIndex]) handleSelect(filtered[selectedIndex]);
              }
            }}
            className="flex-1 bg-transparent text-[13px] text-slate-900 placeholder-slate-400 outline-none"
          />
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 p-1 rounded-md hover:bg-slate-200/50 transition-colors">
            <X className="w-4 h-4" strokeWidth={2} />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-1.5 space-y-0.5">
          {filtered.length === 0 ? (
            <div className="py-8 text-center text-[12px] text-slate-400 font-mono">
              No matches found for "{query}"
            </div>
          ) : (
            filtered.map((item, idx) => {
              const Icon = item.icon;
              const isSelected = idx === selectedIndex;
              return (
                <div
                  key={item.id}
                  onClick={() => handleSelect(item)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`flex items-center justify-between px-3 py-2 rounded-xl cursor-pointer text-xs transition-colors ${
                    isSelected ? 'bg-blue-50/80 text-blue-950 font-medium' : 'text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                      isSelected ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-500'
                    }`}>
                      <Icon className="w-4 h-4" strokeWidth={1.8} />
                    </div>
                    <div className="truncate">
                      <div className="truncate font-medium">{item.title}</div>
                      {item.subtitle && (
                        <div className="text-[11px] text-slate-400 truncate">{item.subtitle}</div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 ml-2">
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-500 border border-slate-200/80 font-mono">
                      {item.category}
                    </span>
                    {isSelected && <ArrowRight className="w-3.5 h-3.5 text-blue-600" />}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer info bar */}
        <div className="px-4 py-2 border-t border-slate-200 bg-slate-50/70 text-[11px] text-slate-500 flex items-center justify-between font-mono">
          <div className="flex items-center gap-3">
            <span>↑↓ to navigate</span>
            <span>↵ to select</span>
            <span>esc to close</span>
          </div>
          <span className="text-blue-600 font-semibold">Perimeter Unified Console</span>
        </div>
      </div>
    </div>
  );
};
