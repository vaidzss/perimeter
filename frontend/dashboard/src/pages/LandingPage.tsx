import React, { useState, useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { LandingNavbar } from '../components/landing/LandingNavbar';
import { LandingHero } from '../components/landing/LandingHero';
import { RouteDiscoveryIceberg } from '../components/landing/RouteDiscoveryIceberg';
import { LiveBolasandbox } from '../components/landing/LiveBolasandbox';
import { GlobalTopologyMap } from '../components/landing/GlobalTopologyMap';
import { ArchitectureBento } from '../components/landing/ArchitectureBento';
import { LandingFooter } from '../components/landing/LandingFooter';
import { DemoDrawer } from '../components/layout/DemoDrawer';

gsap.registerPlugin(ScrollTrigger);

export const LandingPage: React.FC = () => {
  const [isDemoDrawerOpen, setIsDemoDrawerOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Keyboard listener for Shift+D to open attack simulator drawer
    const handleKeyDown = (e: KeyboardEvent) => {
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

  // GSAP Animations: Hero entrance stagger & Section scroll reveals
  useEffect(() => {
    if (!containerRef.current) return;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) return;

    const ctx = gsap.context(() => {
      // 1. Hero Stagger Entrance
      const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
      tl.fromTo(
        '.hero-pill',
        { y: -16, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.6 }
      )
        .fromTo(
          '.hero-title-line',
          { y: 24, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.8, stagger: 0.12 },
          '-=0.3'
        )
        .fromTo(
          '.hero-subtitle',
          { y: 16, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.6 },
          '-=0.4'
        )
        .fromTo(
          '.hero-cta-btn',
          { y: 12, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.5, stagger: 0.1 },
          '-=0.3'
        )
        .fromTo(
          '.hero-canvas-card',
          { y: 30, opacity: 0, scale: 0.98 },
          { y: 0, opacity: 1, scale: 1, duration: 0.8 },
          '-=0.4'
        );

      // 2. ScrollTrigger reveals for sections
      const sections = ['#iceberg', '#sandbox', '#topology', '#architecture'];
      sections.forEach((selector) => {
        const el = document.querySelector(selector);
        if (el) {
          gsap.fromTo(
            el,
            { y: 28, opacity: 0 },
            {
              y: 0,
              opacity: 1,
              duration: 0.7,
              ease: 'power2.out',
              scrollTrigger: {
                trigger: el,
                start: 'top 85%',
                toggleActions: 'play none none none',
              },
            }
          );
        }
      });
    }, containerRef);

    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef} className="min-h-screen bg-[#FAFAFA] text-slate-900 selection:bg-blue-100 selection:text-blue-900 overflow-x-hidden font-sans">
      {/* Floating Light Glass Navbar */}
      <LandingNavbar onOpenDemoDrawer={() => setIsDemoDrawerOpen(true)} />

      {/* Hero Section with Interactive Mesh Canvas */}
      <LandingHero onOpenDemoDrawer={() => setIsDemoDrawerOpen(true)} />

      {/* Route Discovery Iceberg Section */}
      <RouteDiscoveryIceberg />

      {/* Interactive Live BOLA & Abuse Sandbox */}
      <LiveBolasandbox />

      {/* Global Edge Topology & Latency Map */}
      <GlobalTopologyMap />

      {/* Architecture & Deterministic Identity Graph Bento */}
      <ArchitectureBento />

      {/* Clean Editorial Footer */}
      <LandingFooter />

      {/* Demo Attack Simulator Drawer (Shift+D) */}
      <DemoDrawer
        isOpen={isDemoDrawerOpen}
        onClose={() => setIsDemoDrawerOpen(false)}
      />
    </div>
  );
};

export default LandingPage;
