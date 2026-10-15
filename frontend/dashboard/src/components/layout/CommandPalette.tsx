import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Database, ShieldAlert, Activity, FileText, X, ArrowRight, Sliders } from 'lucide-react';
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
  icon: any;
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
    { id: 'p-overview', title: 'Security Posture & Overview', category: 'Pages', route: '/', icon: ShieldAlert },
    { id: 'p-inventory', title: 'API Inventory (All Endpoints)', category: 'Pages', route: '/inventory', icon: Database },
    { id: 'p-shadow', title: 'Shadow APIs Filtered', category: 'Pages', route: '/inventory?status=shadow', icon: Database },
    { id: 'p-alerts', title: 'Security Threat Alerts', category: 'Pages', route: '/alerts', icon: ShieldAlert },
    { id: 'p-traffic', title: 'Traffic Telemetry & Baselines', category: 'Pages', route: '/traffic', icon: Activity },
    { id: 'p-eval', title: 'Detector Benchmark Evaluation', category: 'Pages', route: '/evaluation', icon: FileText },
    { id: 'p-demo', title: 'Demo Controls Drawer (Shift+D)', category: 'Actions', action: () => { onClose(); onOpenDemoDrawer(); }, icon: Sliders },
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

  const handleSelect = (item: any) => {
    onClose();
    if (item.action) {
      item.action();
    } else if (item.route) {
      navigate(item.route);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-black/60 backdrop-blur-xs p-4">
      <div className="w-full max-w-xl rounded-[6px] bg-[#15181D] border border-[#252A31] shadow-2xl overflow-hidden flex flex-col text-[#E6E8EB]">
        {/* Search Input Bar */}
        <div className="flex items-center px-3 py-2.5 border-b border-[#252A31] gap-2">
          <Search className="w-4 h-4 text-[#8B929C] shrink-0" strokeWidth={1.5} />
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
            className="flex-1 bg-transparent text-[13px] text-[#E6E8EB] placeholder-[#8B929C] outline-hidden"
          />
          <button onClick={onClose} className="text-[#8B929C] hover:text-[#E6E8EB] p-1">
            <X className="w-4 h-4" strokeWidth={1.5} />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-1.5 space-y-0.5">
          {filtered.length === 0 ? (
            <div className="py-8 text-center text-[12px] text-[#8B929C]">
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
                  className={`flex items-center justify-between px-3 py-2 rounded-[4px] cursor-pointer text-[13px] transition-colors ${
                    isSelected ? 'bg-[#1C2026] text-[#E6E8EB]' : 'text-[#8B929C] hover:text-[#E6E8EB]'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Icon className="w-3.5 h-3.5 shrink-0 text-[#8B929C]" strokeWidth={1.5} />
                    <div className="min-w-0 truncate">
                      <div className="font-normal text-[#E6E8EB] truncate">{item.title}</div>
                      {item.subtitle && (
                        <div className="text-[11px] text-[#8B929C] font-mono truncate">{item.subtitle}</div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-[11px] text-[#8B929C]">{item.category}</span>
                    <ArrowRight className="w-3 h-3 text-[#8B929C]" strokeWidth={1.5} />
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="px-3 py-1.5 border-t border-[#252A31] bg-[#0E1013] flex items-center justify-between text-[11px] text-[#8B929C]">
          <span>Use <kbd className="px-1 py-0.5 rounded bg-[#15181D] border border-[#252A31]">↑</kbd> <kbd className="px-1 py-0.5 rounded bg-[#15181D] border border-[#252A31]">↓</kbd> to navigate</span>
          <span><kbd className="px-1 py-0.5 rounded bg-[#15181D] border border-[#252A31]">Esc</kbd> to close</span>
        </div>
      </div>
    </div>
  );
};
