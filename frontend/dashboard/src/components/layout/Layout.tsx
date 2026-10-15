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
        setIsCommandPaletteOpen(prev => !prev);
      }
      if (e.shiftKey && (e.key === 'D' || e.key === 'd')) {
        // Prevent typing Shift+D into inputs triggering drawer
        const activeTag = document.activeElement?.tagName.toLowerCase();
        if (activeTag !== 'input' && activeTag !== 'textarea') {
          e.preventDefault();
          setIsDemoDrawerOpen(prev => !prev);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="min-h-screen bg-[#0E1013] text-[#E6E8EB] flex flex-col font-sans selection:bg-[#4C8DFF] selection:text-white">
      {/* 40px Top bar */}
      <Header
        onOpenCommandPalette={() => setIsCommandPaletteOpen(true)}
        onOpenDemoDrawer={() => setIsDemoDrawerOpen(true)}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Slim left nav */}
        <Sidebar onOpenDemoDrawer={() => setIsDemoDrawerOpen(true)} />

        {/* Main Content Area */}
        <main className="flex-1 p-5 overflow-y-auto max-w-[1600px] w-full">
          <Breadcrumbs />
          <Outlet />
        </main>
      </div>

      {/* Freshness & scope footer */}
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
