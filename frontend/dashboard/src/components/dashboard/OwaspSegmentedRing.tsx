import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { mapAlertsToOwaspRing, OwaspArcSegment } from './mappers';
import { ArrowRight, ShieldAlert } from 'lucide-react';

interface OwaspSegmentedRingProps {
  alertTypes: { type: string; count: number; key: string }[];
  totalAlerts?: number;
  onSelectCategory?: (key: string) => void;
}

export const OwaspSegmentedRing: React.FC<OwaspSegmentedRingProps> = ({
  alertTypes,
  totalAlerts = 15,
  onSelectCategory,
}) => {
  const navigate = useNavigate();
  const [hoveredSegment, setHoveredSegment] = useState<OwaspArcSegment | null>(null);

  // Modern clean palette for light mode (crimson, amber, cobalt blue, sky, emerald)
  const segmentColors = ['#E11D48', '#D97706', '#2563EB', '#0284C7', '#059669'];

  const segments = mapAlertsToOwaspRing(alertTypes, 90, 90, 74, 52).map((seg, i) => ({
    ...seg,
    color: segmentColors[i % segmentColors.length],
  }));

  const handleClick = (seg: OwaspArcSegment) => {
    if (onSelectCategory) {
      onSelectCategory(seg.key);
    } else {
      navigate(`/alerts?type=${seg.key}`);
    }
  };

  return (
    <div className="relative border border-slate-200 rounded-2xl bg-white p-5 select-none flex flex-col justify-between shadow-xs h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <div>
            <h3 className="text-[14px] font-semibold text-slate-900 tracking-tight">
              OWASP Top 10 API Threat Coverage
            </h3>
            <p className="text-[12px] text-slate-500 mt-0.5">Distribution across threat families</p>
          </div>
          <span className="text-[11px] font-mono font-medium text-slate-400">Click to filter</span>
        </div>

        <div className="flex flex-col sm:flex-row items-center gap-6 my-2">
          {/* Segmented Ring SVG */}
          <div className="relative w-[180px] h-[180px] shrink-0 flex items-center justify-center">
            <svg width="180" height="180" className="block">
              {segments.map((seg) => {
                const isHovered = hoveredSegment?.key === seg.key;
                return (
                  <path
                    key={seg.key}
                    d={seg.pathData}
                    fill={seg.color}
                    opacity={isHovered ? 1 : 0.85}
                    className="cursor-pointer transition-all duration-200"
                    onMouseEnter={() => setHoveredSegment(seg)}
                    onMouseLeave={() => setHoveredSegment(null)}
                    onClick={() => handleClick(seg)}
                    style={{
                      transform: isHovered ? 'scale(1.03)' : 'scale(1)',
                      transformOrigin: '90px 90px',
                    }}
                  />
                );
              })}
            </svg>

            {/* Central Badge */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-2xl font-bold text-slate-900 font-mono tracking-tight leading-none">
                {totalAlerts}
              </span>
              <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wider mt-1">
                Detections
              </span>
            </div>
          </div>

          {/* Interactive Legend List */}
          <div className="flex-1 w-full space-y-1.5">
            {segments.map((seg) => {
              const isHovered = hoveredSegment?.key === seg.key;
              return (
                <div
                  key={seg.key}
                  onMouseEnter={() => setHoveredSegment(seg)}
                  onMouseLeave={() => setHoveredSegment(null)}
                  onClick={() => handleClick(seg)}
                  className={`flex items-center justify-between p-2 rounded-xl text-xs cursor-pointer transition-all ${
                    isHovered
                      ? 'bg-slate-100/80 shadow-2xs'
                      : 'hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2 truncate pr-2">
                    <span
                      className="w-2.5 h-2.5 rounded-full shrink-0"
                      style={{ backgroundColor: seg.color }}
                    />
                    <span className="truncate font-medium text-slate-800">{seg.label}</span>
                  </div>
                  <span className="font-mono text-slate-500 font-bold text-[11px] shrink-0">
                    {seg.count}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
        <span className="font-mono">Real-time classification</span>
        <button
          onClick={() => navigate('/alerts')}
          className="hover:text-blue-600 font-semibold flex items-center gap-1 transition-colors"
        >
          <span>View all alerts</span>
          <ArrowRight className="w-3 h-3" />
        </button>
      </div>
    </div>
  );
};
