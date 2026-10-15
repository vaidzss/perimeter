import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShieldCheck,
  Database,
  GitBranch,
  Activity,
  ShieldAlert,
  Users,
  BarChart3,
  SlidersHorizontal,
  PanelLeftClose,
  PanelLeftOpen,
} from 'lucide-react';
import { useDashboardMetrics } from '../../api/metrics';
import { useSidebar } from '../../context/SidebarContext';

interface SidebarProps {
  onOpenDemoDrawer: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onOpenDemoDrawer }) => {
  const { isCollapsed, toggleSidebar } = useSidebar();
  const { shadowCount, criticalAlerts } = useDashboardMetrics();

  const navItems = [
    {
      to: '/overview',
      label: 'Security Posture',
      sublabel: 'Overview & Telemetry',
      icon: ShieldCheck,
      badge: null,
      badgeColor: '',
    },
    {
      to: '/inventory',
      label: 'API Inventory',
      sublabel: 'Catalog & Specs',
      icon: Database,
      badge: null,
      badgeColor: '',
    },
    {
      to: '/inventory?status=shadow',
      label: 'Shadow API Drift',
      sublabel: 'Undocumented routes',
      icon: GitBranch,
      badge: shadowCount > 0 ? `${shadowCount}` : null,
      badgeColor: 'border-amber-200 text-amber-800 bg-amber-50',
    },
    {
      to: '/traffic',
      label: 'Traffic Telemetry',
      sublabel: 'Velocity & Latency',
      icon: Activity,
      badge: null,
      badgeColor: '',
    },
    {
      to: '/alerts',
      label: 'Threat Alerts',
      sublabel: 'Live Detections',
      icon: ShieldAlert,
      badge: criticalAlerts > 0 ? `${criticalAlerts}` : null,
      badgeColor: 'border-red-200 text-red-700 bg-red-50',
    },
    {
      to: '/identity',
      label: 'Identity & Access',
      sublabel: 'Actors & Tokens',
      icon: Users,
      badge: null,
      badgeColor: '',
    },
    {
      to: '/evaluation',
      label: 'Benchmarks',
      sublabel: 'F1 & Confusion Matrix',
      icon: BarChart3,
      badge: null,
      badgeColor: '',
    },
  ];

  return (
    <aside
      className={`bg-white border-r border-slate-200 flex flex-col justify-between shrink-0 select-none min-h-[calc(100vh-56px)] z-30 transition-all duration-300 ease-in-out ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Top Nav Rail / Menu Items */}
      <div className="py-3 px-2 flex flex-col space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `relative group flex items-center rounded-xl transition-all ${
                  isCollapsed ? 'justify-center w-11 h-11 mx-auto' : 'px-3 py-2.5 gap-3'
                } ${
                  isActive
                    ? 'bg-blue-50/80 text-blue-700 font-semibold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={`w-5 h-5 shrink-0 transition-colors ${
                      isActive ? 'text-blue-600' : 'text-slate-500 group-hover:text-slate-800'
                    }`}
                    strokeWidth={isActive ? 2.2 : 1.75}
                  />

                  {/* Expanded Label and Sublabel */}
                  {!isCollapsed && (
                    <div className="flex-1 min-w-0">
                      <div className="text-[13px] tracking-tight leading-snug truncate">
                        {item.label}
                      </div>
                      <div className="text-[11px] font-normal text-slate-400 truncate leading-none mt-0.5">
                        {item.sublabel}
                      </div>
                    </div>
                  )}

                  {/* Badge */}
                  {item.badge && (
                    <span
                      className={`font-mono font-bold text-[10px] px-1.5 py-0.5 rounded-full border leading-tight shrink-0 ${item.badgeColor} ${
                        isCollapsed ? 'absolute -top-1 -right-1' : ''
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}

                  {/* Collapsed Tooltip Hover Popover */}
                  {isCollapsed && (
                    <div className="absolute left-full ml-3 px-3 py-1.5 bg-slate-900 text-white text-xs rounded-lg shadow-xl whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-opacity z-50 flex items-center gap-2">
                      <span className="font-medium">{item.label}</span>
                      {item.badge && (
                        <span className={`text-[10px] px-1.5 py-0.2 rounded font-mono font-semibold ${item.badgeColor}`}>
                          {item.badge}
                        </span>
                      )}
                    </div>
                  )}

                  {/* Active Indicator Bar */}
                  {isActive && (
                    <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 rounded-r-full bg-blue-600" />
                  )}
                </>
              )}
            </NavLink>
          );
        })}
      </div>

      {/* Bottom Controls: Attack Simulator Drawer Trigger & Collapse Sidebar Toggle */}
      <div className="p-2 border-t border-slate-200 flex flex-col space-y-1">
        {/* Simulator Drawer Trigger */}
        <button
          onClick={onOpenDemoDrawer}
          title="Open Red-Team Attack Simulator (Shift+D)"
          className={`relative group flex items-center rounded-xl transition-all ${
            isCollapsed ? 'justify-center w-11 h-11 mx-auto' : 'px-3 py-2.5 gap-3'
          } text-slate-600 hover:text-amber-700 hover:bg-amber-50/70 border border-transparent hover:border-amber-200`}
        >
          <SlidersHorizontal className="w-5 h-5 text-amber-600 shrink-0" strokeWidth={1.75} />
          {!isCollapsed && (
            <div className="flex-1 text-left min-w-0">
              <div className="text-[13px] font-medium text-slate-700 truncate leading-snug">
                Attack Simulator
              </div>
              <div className="text-[11px] text-slate-400 font-mono">Shift+D trigger</div>
            </div>
          )}
          {isCollapsed && (
            <div className="absolute left-full ml-3 px-3 py-1.5 bg-slate-900 text-white text-xs rounded-lg shadow-xl whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-opacity z-50">
              Attack Simulator (Shift+D)
            </div>
          )}
        </button>

        {/* Sidebar Collapse Toggle Button */}
        <button
          onClick={toggleSidebar}
          title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          className={`flex items-center rounded-xl text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-colors ${
            isCollapsed ? 'justify-center w-11 h-11 mx-auto' : 'px-3 py-2 gap-3 w-full'
          }`}
        >
          {isCollapsed ? (
            <PanelLeftOpen className="w-5 h-5" strokeWidth={1.75} />
          ) : (
            <>
              <PanelLeftClose className="w-5 h-5" strokeWidth={1.75} />
              <span className="text-[12px] font-medium text-slate-600">Collapse menu</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
};
