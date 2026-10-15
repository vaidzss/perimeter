import React, { useState, useRef, useEffect, useMemo } from 'react';
import gsap from 'gsap';
import { mapTrafficToPulseLine, PulseDataPoint } from './mappers';

interface PulseLineTrafficChartProps {
  data: { timestamp: string; count?: number; requests_per_min?: number; error_rate?: number }[];
  height?: number;
  showAnomalies?: boolean;
  interactive?: boolean;
  title?: string;
  subtitle?: string;
  windowLabel?: string;
}

export const PulseLineTrafficChart: React.FC<PulseLineTrafficChartProps> = ({
  data,
  height = 220,
  showAnomalies = true,
  interactive = true,
  title = 'Traffic Velocity & Baseline Deviation',
  subtitle = 'Requests per minute with dynamic anomaly detection corridor',
  windowLabel = 'Last 1 Hour',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const pulsePathRef = useRef<SVGPathElement>(null);
  const [activeWindow, setActiveWindow] = useState('1h');
  const [dimensions, setDimensions] = useState({ width: 600, height });
  const [hoveredPoint, setHoveredPoint] = useState<PulseDataPoint | null>(null);
  const [mousePos, setMousePos] = useState<{ x: number; y: number } | null>(null);

  // ResizeObserver for responsive SVG dimensions
  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.contentRect.width > 0) {
          setDimensions({
            width: entry.contentRect.width,
            height,
          });
        }
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [height]);

  const chart = useMemo(() => {
    return mapTrafficToPulseLine(
      data,
      dimensions.width,
      dimensions.height,
      { top: 20, right: 28, bottom: 28, left: 45 }
    );
  }, [data, dimensions.width, dimensions.height]);

  // GSAP initial draw-on animation
  useEffect(() => {
    if (!pulsePathRef.current) return;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    const length = pulsePathRef.current.getTotalLength?.() || 1000;
    gsap.fromTo(
      pulsePathRef.current,
      { strokeDasharray: length, strokeDashoffset: length },
      { strokeDashoffset: 0, duration: 0.9, ease: 'power2.out' }
    );
  }, [chart.pulsePath]);

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!interactive || !containerRef.current || chart.points.length === 0) return;
    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    setMousePos({ x: mouseX, y: mouseY });

    // Find nearest point along x axis
    let nearest = chart.points[0];
    let minDist = Math.abs(mouseX - nearest.x);
    for (let i = 1; i < chart.points.length; i++) {
      const dist = Math.abs(mouseX - chart.points[i].x);
      if (dist < minDist) {
        minDist = dist;
        nearest = chart.points[i];
      }
    }
    setHoveredPoint(nearest);
  };

  const handleMouseLeave = () => {
    setHoveredPoint(null);
    setMousePos(null);
  };

  // Generate Area Gradient Fill Path
  const areaFillPath = useMemo(() => {
    if (!chart.pulsePath || chart.points.length < 2) return null;
    const first = chart.points[0];
    const last = chart.points[chart.points.length - 1];
    const bottomY = dimensions.height - 28;
    return `${chart.pulsePath} L ${last.x} ${bottomY} L ${first.x} ${bottomY} Z`;
  }, [chart.pulsePath, chart.points, dimensions.height]);

  return (
    <div ref={containerRef} className="relative w-full select-none bg-white border border-slate-200 rounded-2xl p-5 shadow-xs">
      {/* Header telemetry & Window Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <h3 className="text-[14px] font-semibold text-slate-900 tracking-tight">
            {title}
          </h3>
          <p className="text-[12px] text-slate-500 mt-0.5">{subtitle}</p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-center">
          <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-[11px] font-medium text-slate-600">
            {['15m', '1h', '6h', '24h'].map((w) => (
              <button
                key={w}
                onClick={() => setActiveWindow(w)}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  activeWindow === w
                    ? 'bg-white text-blue-700 font-semibold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {w}
              </button>
            ))}
          </div>

          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-700 text-[11px] font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse" />
            <span>Telemetry Live</span>
          </div>
        </div>
      </div>

      {/* Light Tactical SVG Canvas Area */}
      <div className="relative border border-slate-200 rounded-xl bg-[#FAFAFA] p-2 overflow-hidden shadow-2xs">
        <svg
          width="100%"
          height={dimensions.height}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="relative z-10 block"
        >
          <defs>
            {/* Soft Glowing Area Gradient for Light Canvas */}
            <linearGradient id="lightTrafficGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2563EB" stopOpacity="0.14" />
              <stop offset="100%" stopColor="#2563EB" stopOpacity="0.0" />
            </linearGradient>

            {/* Subtle Baseline Corridor Gradient */}
            <linearGradient id="lightBaselineGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#E2E8F0" stopOpacity="0.45" />
              <stop offset="100%" stopColor="#F1F5F9" stopOpacity="0.2" />
            </linearGradient>
          </defs>

          {/* Clean Horizontal Gridlines & Y-Axis Labels */}
          {[0, 0.5, 1].map((pct) => {
            const val = Math.round(chart.minCount + (chart.maxCount - chart.minCount) * (1 - pct));
            const y = 20 + pct * (dimensions.height - 48);
            return (
              <g key={pct}>
                <line
                  x1={40}
                  y1={y}
                  x2={dimensions.width - 20}
                  y2={y}
                  stroke="#E2E8F0"
                  strokeWidth="1"
                />
                <text
                  x={36}
                  y={y + 3.5}
                  textAnchor="end"
                  fill="#64748B"
                  fontSize="10"
                  fontFamily="monospace"
                  fontWeight="500"
                >
                  {val.toLocaleString()}
                </text>
              </g>
            );
          })}

          {/* 1. Shaded Baseline Band (Expected nominal range) */}
          {chart.baselineBandPath && (
            <path
              d={chart.baselineBandPath}
              fill="url(#lightBaselineGrad)"
              stroke="#CBD5E1"
              strokeWidth="1"
              strokeDasharray="3 3"
            />
          )}

          {/* 2. Soft Gradient Area Fill */}
          {areaFillPath && (
            <path
              d={areaFillPath}
              fill="url(#lightTrafficGrad)"
            />
          )}

          {/* 3. Live Traffic Line */}
          {chart.pulsePath && (
            <path
              ref={pulsePathRef}
              d={chart.pulsePath}
              fill="none"
              stroke="#2563EB"
              strokeWidth="2.2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}

          {/* 4. Normal Data Dots */}
          {chart.points.map((p) => (
            <circle
              key={p.index}
              cx={p.x}
              cy={p.y}
              r={p.isAnomaly ? 4 : 2.5}
              fill={p.isAnomaly ? '#DC2626' : '#2563EB'}
              stroke="#FFFFFF"
              strokeWidth="1.5"
            />
          ))}

          {/* 5. Anomaly Spike Markers */}
          {showAnomalies &&
            chart.anomalies.map((a) => (
              <g key={`pin-${a.index}`} className="pointer-events-none">
                {/* Vertical Dotted Line */}
                <line
                  x1={a.x}
                  y1={14}
                  x2={a.x}
                  y2={dimensions.height - 24}
                  stroke="#DC2626"
                  strokeWidth="1"
                  strokeDasharray="2 3"
                  opacity="0.8"
                />

                {/* Pill Flag */}
                <rect
                  x={Math.min(a.x - 44, dimensions.width - 96)}
                  y={4}
                  width="88"
                  height="18"
                  fill="#FEF2F2"
                  stroke="#FECACA"
                  strokeWidth="1"
                  rx="9"
                />
                <text
                  x={Math.min(a.x, dimensions.width - 52)}
                  y={16.5}
                  textAnchor="middle"
                  fill="#991B1B"
                  fontSize="9.5"
                  fontWeight="600"
                  fontFamily="Inter, sans-serif"
                >
                  ⚡ {a.anomalyLabel || 'Burst Anomaly'}
                </text>
              </g>
            ))}

          {/* 6. Hairline Crosshair on Hover */}
          {interactive && mousePos && hoveredPoint && (
            <g className="pointer-events-none">
              <line
                x1={hoveredPoint.x}
                y1={10}
                x2={hoveredPoint.x}
                y2={dimensions.height - 24}
                stroke="#94A3B8"
                strokeWidth="1"
                strokeDasharray="2 2"
              />
              <circle
                cx={hoveredPoint.x}
                cy={hoveredPoint.y}
                r="5"
                fill="#2563EB"
                stroke="#FFFFFF"
                strokeWidth="2"
              />
            </g>
          )}

          {/* X-Axis Ticks & Timestamps */}
          {chart.points.map((p) => (
            <g key={`x-${p.index}`}>
              <text
                x={p.x}
                y={dimensions.height - 6}
                textAnchor="middle"
                fill="#64748B"
                fontSize="10"
                fontFamily="monospace"
                fontWeight="500"
              >
                {p.timestamp}
              </text>
            </g>
          ))}
        </svg>

        {/* Floating Tooltip HUD on Hover (Crisp White Card) */}
        {interactive && hoveredPoint && (
          <div
            className="absolute z-20 pointer-events-none bg-white border border-slate-200 rounded-xl p-3 text-[11.5px] font-sans shadow-xl text-slate-900"
            style={{
              left: Math.min(hoveredPoint.x + 12, dimensions.width - 170),
              top: Math.max(10, hoveredPoint.y - 50),
            }}
          >
            <div className="flex items-center justify-between gap-3 text-slate-500 text-[10.5px]">
              <span>{hoveredPoint.timestamp} UTC</span>
              {hoveredPoint.isAnomaly ? (
                <span className="text-red-700 font-bold bg-red-50 border border-red-200 px-1.5 py-0.2 rounded">
                  Deviation
                </span>
              ) : (
                <span className="text-emerald-700 font-medium bg-emerald-50 border border-emerald-200 px-1.5 py-0.2 rounded">
                  Nominal
                </span>
              )}
            </div>
            <div className="text-slate-900 font-bold text-[13px] mt-1 font-mono">
              {hoveredPoint.count.toLocaleString()}{' '}
              <span className="text-[11px] text-slate-500 font-normal">req/min</span>
            </div>
            <div className="text-[10px] text-slate-500 mt-0.5 font-mono">
              Corridor: {Math.round(hoveredPoint.baselineLower)}–{Math.round(hoveredPoint.baselineUpper)} req/min
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
