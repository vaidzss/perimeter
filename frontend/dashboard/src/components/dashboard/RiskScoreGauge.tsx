import React from 'react';
import { ShieldCheck, AlertTriangle, AlertCircle } from 'lucide-react';

interface RiskScoreGaugeProps {
  score: number; // 0-100
  grade?: string;
  formula?: string;
  criticalCount: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
  totalAlerts: number;
}

export const RiskScoreGauge: React.FC<RiskScoreGaugeProps> = ({
  score,
  grade = 'Grade B-',
  formula,
  criticalCount,
  highCount,
  mediumCount,
  lowCount,
  totalAlerts,
}) => {
  // SVG Ring geometry
  const size = 160;
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const getScoreColor = () => {
    if (score >= 85) return '#059669'; // Emerald
    if (score >= 60) return '#D97706'; // Amber
    return '#DC2626'; // Red
  };

  const getGradeStyle = () => {
    if (score >= 85) return 'bg-emerald-50 text-emerald-800 border-emerald-200';
    if (score >= 60) return 'bg-amber-50 text-amber-800 border-amber-200';
    return 'bg-rose-50 text-rose-800 border-rose-200';
  };

  const sumSeverities = criticalCount + highCount + mediumCount + lowCount;
  const totalSeverities = sumSeverities > 0 ? sumSeverities : (totalAlerts > 0 ? totalAlerts : 1);
  const critPct = (criticalCount / totalSeverities) * 100;
  const highPct = (highCount / totalSeverities) * 100;
  const medPct = (mediumCount / totalSeverities) * 100;
  const lowPct = (lowCount / totalSeverities) * 100;

  return (
    <div className="relative border border-slate-200 rounded-2xl bg-white p-5 select-none flex flex-col justify-between shadow-xs h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <div>
            <h3 className="text-[14px] font-semibold text-slate-900 tracking-tight">
              Security Posture Score
            </h3>
            <p className="text-[12px] text-slate-500 mt-0.5">Composite risk rating</p>
          </div>
          <span className={`px-2.5 py-0.5 rounded-full border text-[11px] font-mono font-bold ${getGradeStyle()}`}>
            {grade}
          </span>
        </div>

        {/* Circular Gauge Graphic */}
        <div className="relative flex flex-col items-center justify-center my-3">
          <div className="relative w-[160px] h-[160px] flex items-center justify-center">
            <svg width={size} height={size} className="rotate-[-90deg]">
              {/* Background Track */}
              <circle
                cx={size / 2}
                cy={size / 2}
                r={radius}
                stroke="#F1F5F9"
                strokeWidth={strokeWidth}
                fill="none"
              />
              {/* Progress Arc */}
              <circle
                cx={size / 2}
                cy={size / 2}
                r={radius}
                stroke={getScoreColor()}
                strokeWidth={strokeWidth}
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="none"
                style={{
                  transition: 'stroke-dashoffset 0.8s ease-out, stroke 0.4s ease',
                }}
              />
            </svg>

            {/* Inner Score Readout */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="font-mono text-4xl font-bold tracking-tight text-slate-900">
                {score}
              </span>
              <span className="text-[10px] font-mono font-semibold uppercase tracking-widest text-slate-400 mt-0.5">
                Out of 100
              </span>
            </div>
          </div>
        </div>

        {/* Severity Breakdown Strip */}
        <div className="space-y-2 mt-4 pt-4 border-t border-slate-100">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500 font-medium">Severity Distribution</span>
            <span className="font-mono text-[11px] text-slate-400">{totalAlerts} Active</span>
          </div>

          <div className="flex h-2 rounded-full overflow-hidden bg-slate-100 gap-0.5">
            <div style={{ width: `${critPct}%` }} className="bg-red-600 rounded-l-full" title={`Critical: ${criticalCount}`} />
            <div style={{ width: `${highPct}%` }} className="bg-amber-500" title={`High: ${highCount}`} />
            <div style={{ width: `${medPct}%` }} className="bg-yellow-400" title={`Medium: ${mediumCount}`} />
            <div style={{ width: `${lowPct}%` }} className="bg-slate-300 rounded-r-full" title={`Low: ${lowCount}`} />
          </div>

          <div className="grid grid-cols-4 gap-1 text-center font-mono text-[10px] pt-1">
            <div className="text-red-700">
              <span className="font-bold">{criticalCount}</span> Crit
            </div>
            <div className="text-amber-700">
              <span className="font-bold">{highCount}</span> High
            </div>
            <div className="text-yellow-700">
              <span className="font-bold">{mediumCount}</span> Med
            </div>
            <div className="text-slate-500">
              <span className="font-bold">{lowCount}</span> Low
            </div>
          </div>
        </div>
      </div>

      {formula && (
        <div className="mt-4 pt-3 border-t border-slate-100 text-[10.5px] font-mono text-slate-400 truncate">
          Formula: {formula}
        </div>
      )}
    </div>
  );
};
