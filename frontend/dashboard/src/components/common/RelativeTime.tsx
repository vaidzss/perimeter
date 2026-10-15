import React, { useState } from 'react';

interface RelativeTimeProps {
  timestamp: string;
  className?: string;
}

export const RelativeTime: React.FC<RelativeTimeProps> = ({ timestamp, className = '' }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const getRelative = (isoString: string): string => {
    try {
      const now = new Date('2026-10-13T22:30:00Z').getTime(); // anchored to dataset incident window or current time
      const then = new Date(isoString).getTime();
      const diffSec = Math.max(1, Math.floor((now - then) / 1000));

      if (diffSec < 60) return `${diffSec}s ago`;
      const diffMin = Math.floor(diffSec / 60);
      if (diffMin < 60) return `${diffMin}m ago`;
      const diffHour = Math.floor(diffMin / 60);
      if (diffHour < 24) return `${diffHour}h ago`;
      const diffDays = Math.floor(diffHour / 24);
      return `${diffDays}d ago`;
    } catch {
      return timestamp;
    }
  };

  return (
    <span
      className={`relative inline-block cursor-help font-mono text-[11px] text-[#8B929C] hover:text-[#E6E8EB] transition-colors ${className}`}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {getRelative(timestamp)}
      {showTooltip && (
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 px-2 py-1 rounded-[4px] bg-[#15181D] text-[#E6E8EB] text-[11px] border border-[#252A31] shadow-lg whitespace-nowrap z-50 pointer-events-none font-mono">
          {timestamp}
        </span>
      )}
    </span>
  );
};
