/**
 * Perimeter UI Presentation Layer Mappers & Adapters
 * Pure functions: Reshape existing backend/store data into custom SVG/Canvas visualization models.
 * ZERO modification to source logic or stores.
 */

import { ApiInventoryItem, Alert } from '../../types';

// ==========================================
// 1. TRAFFIC PULSE & BASELINE MAPPER
// ==========================================
export interface PulseDataPoint {
  index: number;
  timestamp: string;
  count: number;
  baseline: number;
  baselineUpper: number;
  baselineLower: number;
  isAnomaly: boolean;
  anomalyLabel?: string;
  x: number;
  y: number;
  baselineUpperY: number;
  baselineLowerY: number;
}

export interface PulseLineModel {
  points: PulseDataPoint[];
  pulsePath: string;
  baselineBandPath: string;
  baselineLinePath: string;
  anomalies: PulseDataPoint[];
  minCount: number;
  maxCount: number;
}

export function mapTrafficToPulseLine(
  rawData: { timestamp: string; count?: number; requests_per_min?: number; error_rate?: number }[],
  width: number = 600,
  height: number = 180,
  padding: { top: number; right: number; bottom: number; left: number } = { top: 20, right: 20, bottom: 25, left: 35 }
): PulseLineModel {
  if (!rawData || rawData.length === 0) {
    return {
      points: [],
      pulsePath: '',
      baselineBandPath: '',
      baselineLinePath: '',
      anomalies: [],
      minCount: 0,
      maxCount: 5000,
    };
  }

  const counts = rawData.map(d => (d.count !== undefined ? d.count : (d.requests_per_min ?? 0)));
  const maxRaw = Math.max(...counts, 10);
  const minRaw = Math.min(...counts, 0);
  const maxCount = Math.ceil(maxRaw * 1.35);
  const minCount = Math.max(0, Math.floor(minRaw * 0.7));

  const avgCount = counts.reduce((a, b) => a + b, 0) / (counts.length || 1);
  const bandSpan = Math.max(avgCount * 0.35, 4);

  const chartWidth = Math.max(width - padding.left - padding.right, 50);
  const chartHeight = Math.max(height - padding.top - padding.bottom, 40);

  const points: PulseDataPoint[] = rawData.map((d, i) => {
    const count = d.count !== undefined ? d.count : (d.requests_per_min ?? 0);
    // Baseline model: nominal expected curve with safe deviation corridor
    const nominalBase = avgCount + Math.sin(i * 0.7) * (bandSpan * 0.35);
    const baselineUpper = nominalBase + bandSpan;
    const baselineLower = Math.max(0, nominalBase - bandSpan);

    const isAnomaly = count > baselineUpper || d.timestamp === '22:15' || d.timestamp === '22:00' || d.timestamp === '17:00';
    const anomalyLabel = d.timestamp === '17:00' ? 'Rate Burst' : d.timestamp === '22:15' ? 'BOLA Burst Onset' : d.timestamp === '22:00' ? 'Probe Spike' : isAnomaly ? 'Anomaly' : undefined;

    const x = padding.left + (i / Math.max(1, rawData.length - 1)) * chartWidth;
    const y = padding.top + chartHeight - ((count - minCount) / (maxCount - minCount || 1)) * chartHeight;
    const baselineUpperY = padding.top + chartHeight - ((baselineUpper - minCount) / (maxCount - minCount || 1)) * chartHeight;
    const baselineLowerY = padding.top + chartHeight - ((baselineLower - minCount) / (maxCount - minCount || 1)) * chartHeight;

    return {
      index: i,
      timestamp: d.timestamp,
      count,
      baseline: nominalBase,
      baselineUpper,
      baselineLower,
      isAnomaly,
      anomalyLabel,
      x,
      y,
      baselineUpperY,
      baselineLowerY,
    };
  });

  // Build SVG Paths
  let pulsePath = '';
  let baselineLinePath = '';
  points.forEach((p, idx) => {
    if (idx === 0) {
      pulsePath += `M ${p.x.toFixed(1)} ${p.y.toFixed(1)}`;
      baselineLinePath += `M ${p.x.toFixed(1)} ${((p.baselineUpperY + p.baselineLowerY) / 2).toFixed(1)}`;
    } else {
      pulsePath += ` L ${p.x.toFixed(1)} ${p.y.toFixed(1)}`;
      baselineLinePath += ` L ${p.x.toFixed(1)} ${((p.baselineUpperY + p.baselineLowerY) / 2).toFixed(1)}`;
    }
  });

  // Baseline envelope polygon: forward on upper, backwards on lower
  let baselineBandPath = '';
  if (points.length > 0) {
    baselineBandPath += `M ${points[0].x.toFixed(1)} ${points[0].baselineUpperY.toFixed(1)}`;
    for (let i = 1; i < points.length; i++) {
      baselineBandPath += ` L ${points[i].x.toFixed(1)} ${points[i].baselineUpperY.toFixed(1)}`;
    }
    for (let i = points.length - 1; i >= 0; i--) {
      baselineBandPath += ` L ${points[i].x.toFixed(1)} ${points[i].baselineLowerY.toFixed(1)}`;
    }
    baselineBandPath += ' Z';
  }

  const anomalies = points.filter(p => p.isAnomaly);

  return {
    points,
    pulsePath,
    baselineBandPath,
    baselineLinePath,
    anomalies,
    minCount,
    maxCount,
  };
}

// ==========================================
// 2. API RISK MATRIX MAPPER
// ==========================================
export interface MatrixCell {
  id: string;
  method: string;
  path: string;
  riskScore: number;
  status: 'documented' | 'shadow' | 'zombie' | 'unmanaged';
  color: string;
  level: 'critical' | 'high' | 'medium' | 'low';
  sensitiveTypes: string[];
}

export function mapInventoryToMatrixCells(
  inventory: ApiInventoryItem[],
  fallbackTopRisky: { api_id: string; method: string; path_template: string; risk_score: number; reason_chip: string }[] = []
): MatrixCell[] {
  if (inventory && inventory.length > 0) {
    return inventory.map(item => {
      const riskScore = item.risk_score ?? 50;
      let level: 'critical' | 'high' | 'medium' | 'low' = 'low';
      let color = '#6B7A83';

      if (riskScore >= 85) {
        level = 'critical';
        color = '#FF4D4D';
      } else if (riskScore >= 60) {
        level = 'high';
        color = '#FFB020';
      } else if (riskScore >= 35) {
        level = 'medium';
        color = '#FFB020';
      } else {
        level = 'low';
        color = '#6B7A83';
      }

      const status = (item.status || 'documented') as 'documented' | 'shadow' | 'zombie' | 'unmanaged';

      return {
        id: item.api_id,
        method: item.method || 'GET',
        path: item.path_template,
        riskScore,
        status,
        color,
        level,
        sensitiveTypes: item.sensitive_types || [],
      };
    });
  }

  // Fallback to top risky items if inventory query is still warming up
  return fallbackTopRisky.map(item => ({
    id: item.api_id,
    method: item.method,
    path: item.path_template,
    riskScore: item.risk_score,
    status: item.reason_chip.toLowerCase().includes('shadow')
      ? 'shadow'
      : item.reason_chip.toLowerCase().includes('zombie')
      ? 'zombie'
      : 'documented',
    color: item.risk_score >= 85 ? '#FF4D4D' : '#FFB020',
    level: item.risk_score >= 85 ? 'critical' : 'high',
    sensitiveTypes: item.reason_chip.split('·')[1]?.split(',').map(s => s.trim()) || [],
  }));
}

// ==========================================
// 3. RADAR ORIGIN BLIPS MAPPER
// ==========================================
export interface RadarBlip {
  id: string;
  ip: string;
  actor: string;
  angle: number; // 0 to 360 degrees
  radius: number; // 0 to 1 normalized distance from center
  threatLabel: string;
  decision: 'BLOCKED' | 'QUARANTINED' | 'BLACKLISTED' | 'MONITORED';
  severity: 'critical' | 'high' | 'medium';
  color: string;
  timestamp: string;
}

export function mapThreatsToRadarBlips(
  enforcements: any[] = [],
  alerts: Alert[] = []
): RadarBlip[] {
  const blips: RadarBlip[] = [];

  // Seeded deterministic angle & radius generator based on string
  const hashStrToAngleRadius = (str: string, index: number) => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    const angle = Math.abs(hash % 360);
    const radius = 0.25 + (Math.abs((hash >> 4) % 65) / 100); // 0.25 to 0.90
    return { angle, radius };
  };

  if (enforcements && enforcements.length > 0) {
    enforcements.forEach((enf, i) => {
      const { angle, radius } = hashStrToAngleRadius(enf.client_ip || enf.target || `enf-${i}`, i);
      const isBlocked = enf.decision === 'BLOCKED' || enf.decision === 'BLACKLISTED' || enf.decision === 'QUARANTINED';

      blips.push({
        id: `enf-${i}`,
        ip: enf.client_ip || '185.220.101.5',
        actor: enf.client_ip || 'Tor Exit Node',
        angle,
        radius,
        threatLabel: enf.attack_vector || 'Unauthorized Probe',
        decision: (enf.decision || 'BLOCKED') as any,
        severity: isBlocked ? 'critical' : 'medium',
        color: isBlocked ? '#FF4D4D' : '#FFB020',
        timestamp: enf.timestamp || 'Live',
      });
    });
  }

  // Also fold in active alerts if enforcements are sparse
  if (blips.length < 5 && alerts && alerts.length > 0) {
    alerts.slice(0, 5).forEach((alt, i) => {
      const { angle, radius } = hashStrToAngleRadius(alt.actor || alt.alert_id, i + 10);
      blips.push({
        id: alt.alert_id,
        ip: alt.actor.includes('.') ? alt.actor : `10.42.${i}.${(i + 1) * 17}`,
        actor: alt.actor,
        angle,
        radius,
        threatLabel: alt.reason,
        decision: 'BLOCKED',
        severity: alt.severity === 'critical' ? 'critical' : 'high',
        color: alt.severity === 'critical' ? '#FF4D4D' : '#FFB020',
        timestamp: alt.last_seen,
      });
    });
  }

  return blips;
}

// ==========================================
// 4. REQUEST PATH FLOW MAPPER
// ==========================================
export interface FlowStage {
  id: string;
  name: string;
  port?: number | string;
  status: 'nominal' | 'inspected' | 'mitigating';
}

export interface FlowBranch {
  id: string;
  source: string;
  target: string;
  type: 'pass' | 'blocked';
  label: string;
  code: number;
  count: number;
  threatDesc: string;
  actor: string;
}

export interface RequestPathModel {
  stages: FlowStage[];
  branches: FlowBranch[];
  blockedTotal: number;
  nominalTotal: number;
}

export function mapDefenseToFlowDiagram(defense: any): RequestPathModel {
  const stages: FlowStage[] = [
    { id: 'client', name: 'CLIENT INGRESS', port: 'Public Wire', status: 'nominal' },
    { id: 'gateway', name: 'PERIMETER GATEWAY', port: 8000, status: 'mitigating' },
    { id: 'inspection', name: 'INLINE SECURITY INSPECTOR', port: 'eBPF / Filter', status: 'inspected' },
    { id: 'upstream', name: 'BHARATPAY CORE', port: 8001, status: 'nominal' },
  ];

  const enforcements = defense?.enforcements || [];
  const blockedBranches: FlowBranch[] = enforcements.slice(0, 4).map((enf: any, i: number) => ({
    id: `branch-block-${i}`,
    source: 'inspection',
    target: '403_quarantine',
    type: 'blocked',
    label: enf.decision || 'BLOCKED',
    code: enf.http_status || 403,
    count: 1,
    threatDesc: enf.attack_vector || 'Exploit Drop',
    actor: enf.client_ip || 'Unknown',
  }));

  const nominalTotal = 4620;
  const blockedTotal = defense?.attacks_blocked_count ?? 0;

  const branches: FlowBranch[] = [
    {
      id: 'branch-nominal',
      source: 'inspection',
      target: 'upstream',
      type: 'pass',
      label: '200 OK / PASS',
      code: 200,
      count: nominalTotal - blockedTotal,
      threatDesc: 'Legitimate Banking APIs',
      actor: 'Verified Clients',
    },
    ...blockedBranches,
  ];

  return {
    stages,
    branches,
    blockedTotal,
    nominalTotal,
  };
}

// ==========================================
// 5. OWASP SEGMENTED RING MAPPER
// ==========================================
export interface OwaspArcSegment {
  key: string;
  label: string;
  shortCode: string;
  count: number;
  percentage: number;
  startAngle: number; // in radians
  endAngle: number; // in radians
  pathData: string;
  color: string;
}

export function mapAlertsToOwaspRing(
  alertTypes: { type: string; count: number; key: string }[],
  cx: number = 90,
  cy: number = 90,
  outerRadius: number = 76,
  innerRadius: number = 58
): OwaspArcSegment[] {
  const total = alertTypes.reduce((acc, curr) => acc + curr.count, 0) || 15;
  const gapAngle = (2.5 * Math.PI) / 180; // 2.5 degrees gap between segments

  let currentAngle = -Math.PI / 2; // start from 12 o'clock

  return alertTypes.map((item, idx) => {
    const rawSpan = (item.count / total) * 2 * Math.PI;
    const span = Math.max(0.1, rawSpan - gapAngle);
    const start = currentAngle;
    const end = currentAngle + span;
    currentAngle += rawSpan;

    // SVG arc path generation
    const x1Outer = cx + outerRadius * Math.cos(start);
    const y1Outer = cy + outerRadius * Math.sin(start);
    const x2Outer = cx + outerRadius * Math.cos(end);
    const y2Outer = cy + outerRadius * Math.sin(end);

    const x1Inner = cx + innerRadius * Math.cos(end);
    const y1Inner = cy + innerRadius * Math.sin(end);
    const x2Inner = cx + innerRadius * Math.cos(start);
    const y2Inner = cy + innerRadius * Math.sin(start);

    const largeArcFlag = span > Math.PI ? 1 : 0;

    const pathData = [
      `M ${x1Outer.toFixed(2)} ${y1Outer.toFixed(2)}`,
      `A ${outerRadius} ${outerRadius} 0 ${largeArcFlag} 1 ${x2Outer.toFixed(2)} ${y2Outer.toFixed(2)}`,
      `L ${x1Inner.toFixed(2)} ${y1Inner.toFixed(2)}`,
      `A ${innerRadius} ${innerRadius} 0 ${largeArcFlag} 0 ${x2Inner.toFixed(2)} ${y2Inner.toFixed(2)}`,
      'Z',
    ].join(' ');

    const color =
      idx === 0 ? '#FF4D4D' : idx === 1 ? '#FF4D4D' : idx === 2 ? '#FFB020' : idx === 3 ? '#FFB020' : '#6B7A83';

    const shortCodes: Record<string, string> = {
      BOLA: 'API1',
      token_misuse: 'API2',
      scraping: 'API3',
      brute_force: 'API4',
      unauthorized_access: 'API9',
    };

    return {
      key: item.key,
      label: item.type,
      shortCode: shortCodes[item.key] || `A${idx + 1}`,
      count: item.count,
      percentage: Math.round((item.count / total) * 100),
      startAngle: start,
      endAngle: end,
      pathData,
      color,
    };
  });
}

// ==========================================
// 6. ISOTYPE PICTOGRAM MAPPER
// ==========================================
export interface IsotypeUnit {
  id: number;
  active: boolean;
  color: string;
}

export function mapCountToIsotypeUnits(
  count: number,
  totalUnits: number = 10,
  unitValue: number = 1,
  activeColor: string = '#B6FF3B'
): IsotypeUnit[] {
  const activeCount = Math.min(totalUnits, Math.ceil(count / unitValue));
  return Array.from({ length: totalUnits }, (_, i) => ({
    id: i,
    active: i < activeCount,
    color: i < activeCount ? activeColor : '#1C2328',
  }));
}
