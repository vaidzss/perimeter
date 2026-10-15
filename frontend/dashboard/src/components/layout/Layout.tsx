import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Sidebar } from './Sidebar';
import { Footer } from './Footer';
import { Breadcrumbs } from './Breadcrumbs';
import { CommandPalette } from './CommandPalette';
import { DemoDrawer } from './DemoDrawer';

export const Layout: React.FC = () => {
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isDemoDrawerOpen, setIsDemoDrawerOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      }
      if (e.shiftKey && (e.key === 'D' || e.key === 'd')) {
        const activeTag = document.activeElement?.tagName.toLowerCase();
        if (activeTag !== 'input' && activeTag !== 'textarea') {
          e.preventDefault();
          setIsDemoDrawerOpen((prev) => !prev);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="min-h-screen bg-[#FAFAFA] text-slate-900 flex flex-col font-sans selection:bg-blue-100 selection:text-blue-900">
      {/* Sleek Command Center Floating Header */}
      <Header
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        onOpenDemoDrawer={() => setIsDemoDrawerOpen(true)}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Collapsible Command Rail Sidebar */}
        <Sidebar onOpenDemoDrawer={() => setIsDemoDrawerOpen(true)} />

        {/* Main Command Operations Content Area */}
        <main className="flex-1 p-5 lg:p-7 overflow-y-auto max-w-[1680px] w-full mx-auto bg-[#FAFAFA]">
          <Breadcrumbs />
          <Outlet />
        </main>
      </div>

      {/* Real-time Telemetry & Freshness Footer */}
      <Footer onOpenDemoDrawer={() => setIsDemoDrawerOpen(true)} />

      {/* Cmd+K Command Palette */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        onOpenDemoDrawer={() => setIsDemoDrawerOpen(true)}
      />

      {/* Shift+D Demo controls drawer */}
      <DemoDrawer
        isOpen={isDemoDrawerOpen}
        onClose={() => setIsDemoDrawerOpen(false)}
      />
    </div>
  );
};
