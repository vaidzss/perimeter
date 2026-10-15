import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { mapInventoryToMatrixCells, MatrixCell } from './mappers';
import { ApiInventoryItem } from '../../types';
import { MethodTag } from '../common/MethodTag';
import { ArrowRight, AlertTriangle } from 'lucide-react';

interface ApiRiskMatrixProps {
  inventory: ApiInventoryItem[];
  topRisky?: { api_id: string; method: string; path_template: string; risk_score: number; reason_chip: string }[];
  totalApis?: number;
}

export const ApiRiskMatrix: React.FC<ApiRiskMatrixProps> = ({
  inventory,
  topRisky = [],
  totalApis = 20,
}) => {
  const [hoveredCell, setHoveredCell] = useState<MatrixCell | null>(null);
  const cells = mapInventoryToMatrixCells(inventory, topRisky);

  // Clean Sparkline generator for table rows in light mode
  const renderSparkline = (score: number) => {
    const width = 64;
    const height = 18;
    const points = [
      `${0},${height - 3}`,
      `${16},${height - (score > 80 ? 10 : 5)}`,
      `${32},${height - (score > 80 ? 8 : 6)}`,
      `${48},${height - (score > 80 ? 14 : 9)}`,
      `${width},${height - (score / 100) * 14}`,
    ].join(' ');

    const strokeColor = score >= 85 ? '#DC2626' : score >= 60 ? '#D97706' : '#64748B';

    return (
      <svg width={width} height={height} className="overflow-visible inline-block">
        <polyline
          fill="none"
          stroke={strokeColor}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          points={points}
        />
        <circle
          cx={width}
          cy={height - (score / 100) * 14}
          r="2.5"
          fill={strokeColor}
        />
      </svg>
    );
  };

  return (
    <div className="relative border border-slate-200 rounded-2xl bg-white p-5 select-none flex flex-col justify-between shadow-xs h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <div>
            <h3 className="text-[14px] font-semibold text-slate-900 tracking-tight">
              Top High-Risk APIs & Vulnerability Matrix
            </h3>
            <p className="text-[12px] text-slate-500 mt-0.5">
              Ranked by exposed sensitive entities and missing authorization controls
            </p>
          </div>
          <Link
            to="/inventory"
            className="text-[11px] font-mono font-medium text-slate-500 hover:text-blue-600 flex items-center gap-1 transition-colors"
          >
            <span>{totalApis} Registered</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Top 4 Priority Risky Endpoints Table */}
        <div className="overflow-x-auto my-2">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 text-slate-400 font-mono text-[10.5px]">
                <th className="pb-2 font-medium">METHOD & PATH</th>
                <th className="pb-2 font-medium hidden sm:table-cell">RISK FACTORS</th>
                <th className="pb-2 font-medium text-right">TREND</th>
                <th className="pb-2 font-medium text-right">SCORE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-sans">
              {topRisky.slice(0, 4).map((api) => (
                <tr
                  key={api.api_id}
                  className="hover:bg-slate-50 transition-colors group cursor-pointer"
                >
                  <td className="py-2.5 pr-2">
                    <Link
                      to={`/inventory/${api.api_id}`}
                      className="flex items-center gap-2 group-hover:text-blue-600 transition-colors"
                    >
                      <MethodTag method={api.method} />
                      <span className="font-mono text-slate-800 font-medium truncate max-w-[180px] sm:max-w-[220px]">
                        {api.path_template}
                      </span>
                    </Link>
                  </td>
                  <td className="py-2.5 hidden sm:table-cell">
                    <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                      {api.reason_chip}
                    </span>
                  </td>
                  <td className="py-2.5 text-right font-mono">{renderSparkline(api.risk_score)}</td>
                  <td className="py-2.5 text-right">
                    <span
                      className={`font-mono text-xs font-bold px-2 py-0.5 rounded ${
                        api.risk_score >= 85
                          ? 'bg-red-50 text-red-700 border border-red-200'
                          : 'bg-amber-50 text-amber-800 border border-amber-200'
                      }`}
                    >
                      {api.risk_score}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Footer Info */}
      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-mono">
        <span>Sensitive Data Auto-Tagging</span>
        <span className="text-amber-800 font-medium">4 Critical Exposures</span>
      </div>
    </div>
  );
};
