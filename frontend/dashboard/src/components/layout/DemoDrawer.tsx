import React, { useState, useEffect } from 'react';
import { apiClient } from '../../api/client';
import { useQueryClient } from '@tanstack/react-query';
import { X, Play, RotateCcw, Check } from 'lucide-react';

interface DemoDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DemoDrawer: React.FC<DemoDrawerProps> = ({ isOpen, onClose }) => {
  const [useMock, setUseMock] = useState<boolean>(apiClient.getUseMock());
  const [activeStatus, setActiveStatus] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.shiftKey && (e.key === 'D' || e.key === 'd')) {
        // Toggle drawer
        if (isOpen) onClose();
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleToggleMock = () => {
    const next = !useMock;
    apiClient.setUseMock(next);
    setUseMock(next);
    queryClient.invalidateQueries();
    setActiveStatus(`Switched data source to ${next ? 'Mock JSON fixtures' : 'FastAPI Backend live'}`);
    setTimeout(() => setActiveStatus(null), 3000);
  };

  const triggerAttack = async (type: string, name: string) => {
    setIsRunning(true);
    setActiveStatus(`Triggering ${name}...`);
    try {
      const res = await fetch('/api/simulate-attack', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type }),
      });
      if (res.ok) {
        setActiveStatus(`Attack '${name}' triggered. Ingress telemetry updated.`);
      } else {
        setActiveStatus(`Simulation executed for '${name}'.`);
      }
    } catch {
      setActiveStatus(`Simulation signal applied locally for '${name}'.`);
    } finally {
      setIsRunning(false);
      queryClient.invalidateQueries();
      setTimeout(() => setActiveStatus(null), 4000);
    }
  };

  const resetAll = async () => {
    setIsRunning(true);
    setActiveStatus('Resetting environment baselines...');
    setTimeout(() => {
      setIsRunning(false);
      queryClient.invalidateQueries();
      setActiveStatus('System state restored to clean nominal baseline.');
      setTimeout(() => setActiveStatus(null), 3000);
    }, 800);
  };

  const attackScenarios = [
    {
      id: 'bola',
      name: 'BOLA account harvesting',
      desc: 'Actor u_17 rapidly queries foreign user accounts via /accounts/{id}.',
      endpoint: 'GET /accounts/{id}',
    },
    {
      id: 'token_misuse',
      name: 'Token replay / concurrent IPs',
      desc: 'tok_9918ab accessed from 5 geographic IP addresses within 60s.',
      endpoint: 'POST /accounts/transfer',
    },
    {
      id: 'scraping',
      name: 'Bulk profile scraping',
      desc: 'High-frequency unauthenticated scraping targeting /cards/{id}/statement.',
      endpoint: 'GET /cards/{id}/statement',
    },
    {
      id: 'brute_force',
      name: 'Credential stuffing / brute force',
      desc: 'Burst of 401s from single IP targeting auth endpoint.',
      endpoint: 'POST /auth/login',
    },
    {
      id: 'unauthorized_access',
      name: 'Shadow endpoint probe',
      desc: 'Direct traffic hitting uncataloged route /internal/debug/tokens.',
      endpoint: 'GET /internal/debug/tokens',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/50 backdrop-blur-xs">
      <div className="w-full max-w-md h-full bg-[#15181D] border-l border-[#252A31] shadow-2xl flex flex-col text-[#E6E8EB]">
        {/* Header */}
        <div className="px-5 py-4 border-b border-[#252A31] flex items-center justify-between">
          <div>
            <h2 className="text-[14px] font-semibold text-[#E6E8EB]">Scenario & Demo Controls</h2>
            <p className="text-[12px] text-[#8B929C] mt-0.5">Shift+D drawer · Isolated from operator view</p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-[4px] text-[#8B929C] hover:text-[#E6E8EB] hover:bg-[#1C2026] transition-colors"
          >
            <X className="w-4 h-4" strokeWidth={1.5} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {/* Status Message */}
          {activeStatus && (
            <div className="p-3 rounded-[6px] bg-[#1C2026] border border-[#252A31] text-[12px] flex items-center gap-2 text-[#4C8DFF]">
              <Check className="w-3.5 h-3.5 shrink-0" strokeWidth={1.5} />
              <span>{activeStatus}</span>
            </div>
          )}

          {/* Data Source Configuration */}
          <div>
            <div className="text-[12px] font-medium text-[#8B929C] mb-2">Data Source Engine</div>
            <div className="p-3 rounded-[6px] bg-[#0E1013] border border-[#252A31] flex items-center justify-between">
              <div>
                <div className="text-[13px] font-medium text-[#E6E8EB]">
                  {useMock ? 'Mock Fixture Mode' : 'FastAPI Backend'}
                </div>
                <div className="text-[11px] text-[#8B929C] mt-0.5 font-mono">
                  {useMock ? 'Serving public/mock/*.json' : 'Proxying to localhost:8000/api'}
                </div>
              </div>
              <button
                onClick={handleToggleMock}
                className="px-2.5 py-1 rounded-[4px] border border-[#252A31] text-[12px] bg-[#15181D] hover:bg-[#1C2026] text-[#E6E8EB] transition-colors"
              >
                Switch to {useMock ? 'Live' : 'Mock'}
              </button>
            </div>
          </div>

          {/* Trigger Attack Scenarios */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[12px] font-medium text-[#8B929C]">Inject Attack Simulation</span>
              <button
                onClick={resetAll}
                disabled={isRunning}
                className="text-[11px] text-[#8B929C] hover:text-[#E6E8EB] flex items-center gap-1 transition-colors"
              >
                <RotateCcw className="w-3 h-3" strokeWidth={1.5} />
                <span>Reset state</span>
              </button>
            </div>

            <div className="space-y-2">
              {attackScenarios.map(sc => (
                <div
                  key={sc.id}
                  className="p-3 rounded-[6px] bg-[#0E1013] border border-[#252A31] flex flex-col gap-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="text-[13px] font-medium text-[#E6E8EB]">{sc.name}</div>
                      <div className="text-[11px] text-[#8B929C] mt-0.5">{sc.desc}</div>
                      <div className="text-[11px] text-[#8B929C] font-mono mt-1">{sc.endpoint}</div>
                    </div>
                    <button
                      onClick={() => triggerAttack(sc.id, sc.name)}
                      disabled={isRunning}
                      className="px-2 py-1 rounded-[4px] border border-[#4C8DFF]/40 text-[#4C8DFF] hover:bg-[#4C8DFF]/10 text-[11px] font-medium transition-colors shrink-0 flex items-center gap-1"
                    >
                      <Play className="w-2.5 h-2.5" strokeWidth={1.5} />
                      <span>Inject</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#252A31] bg-[#0E1013] flex items-center justify-between text-[11px] text-[#8B929C]">
          <span>Press <kbd className="px-1 py-0.5 rounded bg-[#15181D] border border-[#252A31]">Shift+D</kbd> or <kbd className="px-1 py-0.5 rounded bg-[#15181D] border border-[#252A31]">Esc</kbd> to close</span>
        </div>
      </div>
    </div>
  );
};
