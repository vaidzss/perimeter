import React from 'react';
import { ShieldAlert, Lock, AlertTriangle, ShieldCheck } from 'lucide-react';

interface IsotypePictogramProps {
  label: string;
  count: number;
  unitValue?: number;
  totalUnits?: number;
  color?: string;
  iconType?: 'shield' | 'lock' | 'warning' | 'square';
  subtext?: string;
}

export const IsotypePictogram: React.FC<IsotypePictogramProps> = ({
  label,
  count,
  unitValue = 1,
  totalUnits = 8,
  color = '#059669',
  iconType = 'shield',
  subtext,
}) => {
  const activeUnits = Math.min(totalUnits, Math.ceil(count / unitValue));

  const getTheme = () => {
    switch (iconType) {
      case 'shield':
        return {
          bg: 'bg-rose-50',
          border: 'border-rose-200',
          text: 'text-rose-700',
          activeDot: 'bg-rose-600',
          icon: <ShieldAlert className="w-4 h-4 text-rose-600" />,
        };
      case 'lock':
        return {
          bg: 'bg-amber-50',
          border: 'border-amber-200',
          text: 'text-amber-800',
          activeDot: 'bg-amber-600',
          icon: <Lock className="w-4 h-4 text-amber-600" />,
        };
      case 'warning':
        return {
          bg: 'bg-amber-50',
          border: 'border-amber-200',
          text: 'text-amber-800',
          activeDot: 'bg-amber-600',
          icon: <AlertTriangle className="w-4 h-4 text-amber-600" />,
        };
      case 'square':
      default:
        return {
          bg: 'bg-emerald-50',
          border: 'border-emerald-200',
          text: 'text-emerald-800',
          activeDot: 'bg-emerald-600',
          icon: <ShieldCheck className="w-4 h-4 text-emerald-600" />,
        };
    }
  };

  const theme = getTheme();

  return (
    <div className="relative border border-slate-200 rounded-2xl bg-white p-4 select-none flex flex-col justify-between shadow-xs hover:border-slate-300 transition-all">
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="text-[12px] font-medium text-slate-500">
            {label}
          </div>
          <div className={`w-7 h-7 rounded-lg flex items-center justify-center border ${theme.bg} ${theme.border}`}>
            {theme.icon}
          </div>
        </div>

        <div className="flex items-baseline gap-2 mb-2">
          <span className="font-mono text-2xl font-bold text-slate-900 tracking-tight">
            {count}
          </span>
          <span className="text-[11px] text-slate-400 font-medium">units</span>
        </div>

        {/* Clean Discrete Dots Indicator */}
        <div className="flex items-center gap-1.5 py-1">
          {Array.from({ length: totalUnits }).map((_, idx) => (
            <span
              key={idx}
              className={`h-1.5 flex-1 rounded-full transition-colors ${
                idx < activeUnits ? theme.activeDot : 'bg-slate-200'
              }`}
            />
          ))}
        </div>
      </div>

      {subtext && (
        <div className="pt-2 mt-2 border-t border-slate-100 text-[11px] text-slate-500 truncate">
          {subtext}
        </div>
      )}
    </div>
  );
};
