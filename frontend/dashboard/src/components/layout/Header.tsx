import React from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../../context/ThemeContext';
import { Search, Sun, Moon, Shield, ChevronDown } from 'lucide-react';

interface HeaderProps {
  onOpenCommandPalette: () => void;
  onOpenDemoDrawer: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenCommandPalette }) => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <header className="h-10 bg-[#15181D] border-b border-[#252A31] px-4 flex items-center justify-between text-[13px] text-[#E6E8EB] select-none sticky top-0 z-40">
      {/* Left: Product Name & Scopes */}
      <div className="flex items-center gap-4">
        <Link to="/" className="flex items-center gap-2 group">
          <Shield className="w-4 h-4 text-[#4C8DFF]" strokeWidth={1.5} />
          <span className="font-semibold text-[13px] tracking-tight text-[#E6E8EB] group-hover:text-white transition-colors">
            Perimeter
          </span>
        </Link>

        <div className="h-4 w-px bg-[#252A31]" />

        {/* Environment selector */}
        <div className="relative flex items-center gap-1.5 text-[12px] text-[#8B929C] hover:text-[#E6E8EB] cursor-pointer">
          <span className="w-1.5 h-1.5 rounded-full bg-[#10b981]" />
          <span>production</span>
          <ChevronDown className="w-3 h-3 text-[#8B929C]" strokeWidth={1.5} />
        </div>

        {/* Time-range picker */}
        <div className="flex items-center gap-1.5 text-[12px] text-[#8B929C] hover:text-[#E6E8EB] cursor-pointer pl-1">
          <span>Last 1 hour</span>
          <ChevronDown className="w-3 h-3 text-[#8B929C]" strokeWidth={1.5} />
        </div>
      </div>

      {/* Center: Command Palette Trigger */}
      <button
        onClick={onOpenCommandPalette}
        className="flex items-center gap-2 px-2.5 py-1 rounded-[4px] bg-[#0E1013] border border-[#252A31] hover:border-[#8B929C]/40 text-[#8B929C] hover:text-[#E6E8EB] text-[12px] transition-colors w-64 justify-between"
      >
        <span className="flex items-center gap-2">
          <Search className="w-3.5 h-3.5" strokeWidth={1.5} />
          <span>Search or jump to...</span>
        </span>
        <kbd className="text-[10px] font-mono px-1 py-0.5 rounded bg-[#15181D] border border-[#252A31]">⌘K</kbd>
      </button>

      {/* Right: Controls & Avatar */}
      <div className="flex items-center gap-3">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          className="p-1 rounded-[4px] text-[#8B929C] hover:text-[#E6E8EB] hover:bg-[#1C2026] transition-colors"
        >
          {isDark ? <Sun className="w-4 h-4" strokeWidth={1.5} /> : <Moon className="w-4 h-4" strokeWidth={1.5} />}
        </button>

        {/* Avatar */}
        <div className="w-6 h-6 rounded-full bg-[#252A31] border border-[#343B45] flex items-center justify-center text-[10px] font-medium text-[#E6E8EB]" title="SecOps Operator">
          SO
        </div>
      </div>
    </header>
  );
};
