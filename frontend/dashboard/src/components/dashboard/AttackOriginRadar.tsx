import React, { useRef, useEffect, useState, useMemo } from 'react';
import { mapThreatsToRadarBlips, RadarBlip } from './mappers';
import { Alert } from '../../types';
import { Crosshair } from 'lucide-react';

interface AttackOriginRadarProps {
  enforcements?: any[];
  alerts?: Alert[];
  size?: number;
  onSelectBlip?: (blip: RadarBlip) => void;
}

export const AttackOriginRadar: React.FC<AttackOriginRadarProps> = ({
  enforcements = [],
  alerts = [],
  size = 230,
  onSelectBlip,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [selectedBlip, setSelectedBlip] = useState<RadarBlip | null>(null);

  const blips = useMemo(() => {
    return mapThreatsToRadarBlips(enforcements, alerts);
  }, [enforcements, alerts]);

  // Clean light-mode radar sweep animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let sweepAngle = 0;
    const sweepSpeed = 0.02;

    const render = () => {
      const width = canvas.width;
      const height = canvas.height;
      const cx = width / 2;
      const cy = height / 2;
      const maxRadius = width / 2 - 16;

      // 1. Pure White Radar Canvas Background
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, width, height);

      // 2. Concentric Range Rings in Hairline Slate (#E2E8F0)
      const rings = [0.33, 0.66, 1.0];
      rings.forEach((pct) => {
        const r = maxRadius * pct;
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.strokeStyle = '#E2E8F0';
        ctx.lineWidth = 1;
        ctx.stroke();

        // Ring distance labels
        ctx.fillStyle = '#94A3B8';
        ctx.font = '9px monospace';
        ctx.fillText(`${Math.round(pct * 100)}%`, cx + 3, cy - r + 11);
      });

      // 3. Crosshair Axes in Slate-200
      ctx.beginPath();
      ctx.moveTo(cx - maxRadius, cy);
      ctx.lineTo(cx + maxRadius, cy);
      ctx.moveTo(cx, cy - maxRadius);
      ctx.lineTo(cx, cy + maxRadius);
      ctx.strokeStyle = '#E2E8F0';
      ctx.lineWidth = 1;
      ctx.stroke();

      // 4. Subtle Cobalt Blue Gradient Sweep Wedge
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, maxRadius, sweepAngle - 0.45, sweepAngle);
      ctx.closePath();

      const sweepGrad = ctx.createRadialGradient(cx, cy, 0, cx, cy, maxRadius);
      sweepGrad.addColorStop(0, 'rgba(37, 99, 235, 0.02)');
      sweepGrad.addColorStop(1, 'rgba(37, 99, 235, 0.14)');
      ctx.fillStyle = sweepGrad;
      ctx.fill();
      ctx.restore();

      // 5. Draw Threat Blips
      blips.forEach((blip) => {
        const bx = cx + (blip.radius / 100) * maxRadius * Math.cos(blip.angle);
        const by = cy + (blip.radius / 100) * maxRadius * Math.sin(blip.angle);

        // Blip Outer Halo
        ctx.beginPath();
        ctx.arc(bx, by, blip.severity === 'critical' ? 7 : 5, 0, Math.PI * 2);
        ctx.fillStyle =
          blip.severity === 'critical'
            ? 'rgba(220, 38, 38, 0.2)'
            : blip.severity === 'high'
            ? 'rgba(217, 119, 6, 0.2)'
            : 'rgba(37, 99, 235, 0.2)';
        ctx.fill();

        // Blip Core Dot
        ctx.beginPath();
        ctx.arc(bx, by, blip.severity === 'critical' ? 4 : 3, 0, Math.PI * 2);
        ctx.fillStyle =
          blip.severity === 'critical'
            ? '#DC2626'
            : blip.severity === 'high'
            ? '#D97706'
            : '#2563EB';
        ctx.fill();
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      });

      sweepAngle += sweepSpeed;
      if (sweepAngle > Math.PI * 2) {
        sweepAngle = 0;
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [blips]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const maxRadius = canvas.width / 2 - 16;

    // Find nearest blip within 14px click radius
    for (const blip of blips) {
      const bx = cx + (blip.radius / 100) * maxRadius * Math.cos(blip.angle);
      const by = cy + (blip.radius / 100) * maxRadius * Math.sin(blip.angle);
      const dist = Math.hypot(x - bx, y - by);
      if (dist < 14) {
        setSelectedBlip(blip);
        if (onSelectBlip) onSelectBlip(blip);
        return;
      }
    }
    setSelectedBlip(null);
  };

  return (
    <div className="relative bg-white border border-slate-200 rounded-2xl p-5 select-none flex flex-col justify-between shadow-xs h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <div>
            <h3 className="text-[14px] font-semibold text-slate-900 tracking-tight">
              Attack Vector & Threat Radar
            </h3>
            <p className="text-[12px] text-slate-500 mt-0.5">Real-time polar threat compass</p>
          </div>
          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-slate-50 border border-slate-200 text-slate-600 font-mono text-[11px]">
            <Crosshair className="w-3.5 h-3.5 text-blue-600" />
            <span>{blips.length} Targets</span>
          </div>
        </div>

        {/* Polar Canvas Surface */}
        <div className="relative flex items-center justify-center my-2">
          <canvas
            ref={canvasRef}
            width={size}
            height={size}
            onClick={handleCanvasClick}
            className="rounded-full cursor-pointer border border-slate-200/80 shadow-2xs"
          />

          {/* Active Blip Popover Card */}
          {selectedBlip && (
            <div className="absolute z-20 -bottom-2 bg-white border border-slate-200 rounded-xl p-3 text-xs shadow-xl max-w-[220px] text-slate-800 animate-in fade-in zoom-in-95 duration-150">
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold font-mono ${
                  selectedBlip.severity === 'critical'
                    ? 'bg-red-50 text-red-700 border border-red-200'
                    : 'bg-amber-50 text-amber-800 border border-amber-200'
                }`}>
                  {selectedBlip.severity.toUpperCase()}
                </span>
                <span className="text-[10px] font-mono text-slate-400">
                  {selectedBlip.ip}
                </span>
              </div>
              <div className="font-semibold text-slate-900 truncate">{selectedBlip.threatLabel}</div>
              <div className="text-[10px] text-blue-600 font-mono mt-1">
                Actor: {selectedBlip.actor}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-mono">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-red-600" /> Critical BOLA
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-amber-500" /> Token Replay
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-blue-600" /> Probing
        </span>
      </div>
    </div>
  );
};
