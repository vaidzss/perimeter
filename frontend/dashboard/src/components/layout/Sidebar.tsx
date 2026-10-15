import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Database,
  Activity,
  ShieldAlert,
  ShieldCheck,
  Search,
  Award,
  Layers,
  Sliders,
  Users
} from 'lucide-react';
import { useDashboardMetrics } from '../../api/metrics';

interface SidebarProps {
  onOpenDemoDrawer: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onOpenDemoDrawer }) => {
  const { shadowCount, criticalAlerts } = useDashboardMetrics();

  const navGroups = [
    {
      group: 'Inventory',
      question: 'Which APIs exist?',
      items: [
        {
          to: '/inventory',
          label: 'API inventory',
          icon: Database,
          badge: null,
        },
        {
          to: '/inventory?status=shadow',
          label: 'Shadow diff',
          icon: Layers,
          badge: shadowCount > 0 ? `${shadowCount}` : null,
          badgeColor: 'text-[#B47AEA] bg-[#B47AEA]/10 border-[#B47AEA]/30',
        },
      ],
    },
    {
      group: 'Behavior',
      question: 'How are they used?',
      items: [
        {
          to: '/traffic',
          label: 'Traffic telemetry',
          icon: Activity,
          badge: null,
        },
      ],
    },
    {
      group: 'Risk',
      question: 'What risk does each pose?',
      items: [
        {
          to: '/alerts',
          label: 'Threat alerts',
          icon: ShieldAlert,
          badge: criticalAlerts > 0 ? `${criticalAlerts}` : null,
          badgeColor: 'text-[#E5484D] bg-[#E5484D]/10 border-[#E5484D]/30',
        },
        {
          to: '/',
          label: 'Posture & scores',
          icon: Search,
          badge: null,
        },
      ],
    },
    {
      group: 'Defense',
      question: 'How is it saved?',
      items: [
        {
          to: '/',
          label: 'Active mitigations',
          icon: ShieldCheck,
          badge: 'SHIELD ON',
          badgeColor: 'text-[#10b981] bg-[#10b981]/10 border-[#10b981]/30',
        },
      ],
    },
    {
      group: 'Identity',
      question: 'Who is authorized?',
      items: [
        {
          to: '/identity',
          label: 'Identity & access',
          icon: Users,
          badge: 'ACTIVE',
          badgeColor: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/30',
        },
      ],
    },
  ];

  const bottomItems = [
    {
      to: '/alerts/alt-01',
      label: 'Investigations',
      icon: Search,
    },
    {
      to: '/evaluation',
      label: 'Evaluation',
      icon: Award,
    },
  ];

  return (
    <aside className="w-56 bg-[#15181D] border-r border-[#252A31] flex flex-col justify-between shrink-0 select-none text-[13px] min-h-[calc(100vh-40px)]">
      <div className="py-3 px-2 space-y-4">
        {navGroups.map((group) => (
          <div key={group.group}>
            <div className="px-2.5 py-1 flex items-baseline justify-between text-[11px] text-[#8B929C]">
              <span className="font-medium text-[#E6E8EB]">{group.group}</span>
              <span className="text-[10px] text-[#8B929C] truncate max-w-[110px]">{group.question}</span>
            </div>
            <nav className="space-y-0.5 mt-0.5">
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.to === '/'}
                    className={({ isActive }) =>
                      `flex items-center justify-between px-2.5 py-1.5 rounded-[4px] text-[12px] transition-colors ${
                        isActive
                          ? 'bg-[#1C2026] text-[#E6E8EB] font-medium'
                          : 'text-[#8B929C] hover:text-[#E6E8EB] hover:bg-[#1C2026]/50'
                      }`
                    }
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <Icon className="w-3.5 h-3.5 shrink-0" strokeWidth={1.5} />
                      <span className="truncate">{item.label}</span>
                    </div>
                    {item.badge && (
                      <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded-[3px] border ${item.badgeColor}`}>
                        {item.badge}
                      </span>
                    )}
                  </NavLink>
                );
              })}
            </nav>
          </div>
        ))}

        <div className="pt-2 border-t border-[#252A31]">
          <div className="px-2.5 py-1 text-[11px] font-medium text-[#E6E8EB]">
            Analysis
          </div>
          <nav className="space-y-0.5 mt-0.5">
            {bottomItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-2.5 py-1.5 rounded-[4px] text-[12px] transition-colors ${
                      isActive
                        ? 'bg-[#1C2026] text-[#E6E8EB] font-medium'
                        : 'text-[#8B929C] hover:text-[#E6E8EB] hover:bg-[#1C2026]/50'
                    }`
                  }
                >
                  <div className="flex items-center gap-2">
                    <Icon className="w-3.5 h-3.5 shrink-0" strokeWidth={1.5} />
                    <span>{item.label}</span>
                  </div>
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Subtle Drawer trigger hint in footer of sidebar */}
      <div className="p-3 border-t border-[#252A31] text-[11px] text-[#8B929C]">
        <button
          onClick={onOpenDemoDrawer}
          className="w-full flex items-center justify-between px-2 py-1.5 rounded-[4px] hover:bg-[#1C2026] text-[#8B929C] hover:text-[#E6E8EB] transition-colors"
        >
          <span className="flex items-center gap-1.5">
            <Sliders className="w-3 h-3 text-[#8B929C]" strokeWidth={1.5} />
            <span>Simulate attacks</span>
          </span>
          <kbd className="text-[10px] font-mono px-1 py-0.2 rounded bg-[#0E1013] border border-[#252A31]">Shift+D</kbd>
        </button>
      </div>
    </aside>
  );
};
