import React, { useState, useEffect } from 'react';

interface RelativeTimeProps {
  timestamp?: string | null;
  className?: string;
}

export const RelativeTime: React.FC<RelativeTimeProps> = ({ timestamp, className = '' }) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const [, setTick] = useState(0);

  // Dynamic ticking every 3 seconds to keep relative times live
  useEffect(() => {
    const timer = setInterval(() => {
      setTick(t => t + 1);
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  if (!timestamp) {
    return <span className={`font-mono text-xs text-slate-400 ${className}`}>Never</span>;
  }

  const getRelative = (isoString: string): string => {
    try {
      const now = Date.now();
      const then = new Date(isoString).getTime();
      if (isNaN(then)) return '—';

      const diffSec = Math.floor((now - then) / 1000);

      if (diffSec < 3) return 'Just now';
      if (diffSec < 60) return `${diffSec}s ago`;
      const diffMin = Math.floor(diffSec / 60);
      if (diffMin < 60) return `${diffMin}m ago`;
      const diffHour = Math.floor(diffMin / 60);
      if (diffHour < 24) return `${diffHour}h ago`;
      const diffDays = Math.floor(diffHour / 24);
      return `${diffDays}d ago`;
    } catch {
      return String(timestamp);
    }
  };

  return (
    <span
      className={`relative inline-block cursor-help font-mono text-xs text-slate-500 hover:text-slate-800 transition-colors ${className}`}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {getRelative(timestamp)}
      {showTooltip && (
        <span className="absolute bottom-full right-0 mb-1.5 px-2.5 py-1 rounded-md bg-slate-900 text-slate-100 text-[11px] border border-slate-800 shadow-xl whitespace-nowrap z-50 pointer-events-none font-mono">
          {timestamp}
        </span>
      )}
    </span>
  );
};
