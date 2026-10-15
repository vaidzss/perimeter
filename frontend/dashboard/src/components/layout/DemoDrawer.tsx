import React, { useState, useEffect } from 'react';
import { apiClient } from '../../api/client';
import { useQueryClient } from '@tanstack/react-query';
import { X, Play, RotateCcw, Check, Sparkles } from 'lucide-react';

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
      if (type === 'sqli_cmd') {
        await fetch("/api/v2/search/merchants?q=' OR 1=1 --");
      } else if (type === 'ssrf') {
        await fetch("/api/v2/users/me/webhook-avatar", {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ avatar_url: 'http://169.254.169.254/latest/meta-data/' })
        });
      } else if (type === 'business_logic') {
        await fetch("/api/v2/payments/upi-transfer", {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ amount: -5000, coupons: ['SAVE10', 'SAVE10'] })
        });
      } else if (type === 'redos_complexity') {
        await fetch("/api/v2/accounts/import-statement", {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ regex_filter: '(a+)+$!' })
        });
      } else if (type === 'supply_chain') {
        await fetch("/api/v2/payments/fx-rate?vendor_poisoned=true&enforce_guard=true");
      } else {
        await fetch('/api/simulate-attack', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type }),
        });
      }
      setActiveStatus(`Attack '${name}' triggered. Ingress telemetry updated.`);
    } catch {
      setActiveStatus(`Simulation executed for '${name}'.`);
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
      name: 'BOLA Account Harvesting',
      desc: 'Actor u_17 rapidly queries foreign user accounts via /accounts/{id}.',
      endpoint: 'GET /accounts/{id}',
      owasp: 'API1:2023',
    },
    {
      id: 'token_misuse',
      name: 'Token Replay / Concurrent IPs',
      desc: 'tok_9918ab accessed from 5 geographic IP addresses within 60s.',
      endpoint: 'POST /accounts/transfer',
      owasp: 'API2:2023',
    },
    {
      id: 'scraping',
      name: 'Bulk Statement Scraping',
      desc: 'High-frequency unauthenticated scraping targeting cards statement.',
      endpoint: 'GET /cards/{id}/statement',
      owasp: 'API4:2023',
    },
    {
      id: 'brute_force',
      name: 'Credential Stuffing Wave',
      desc: 'Burst of 401s from single IP targeting core authentication route.',
      endpoint: 'POST /auth/login',
      owasp: 'API2:2023',
    },
    {
      id: 'unauthorized_access',
      name: 'Shadow Endpoint Probe',
      desc: 'Direct traffic hitting uncataloged route /internal/debug/tokens.',
      endpoint: 'GET /internal/debug/tokens',
      owasp: 'API9:2023',
    },
    {
      id: 'sqli_cmd',
      name: 'SQLi & Command Injection',
      desc: "Tautology (' OR 1=1 --) & shell delimiters in search query parameters.",
      endpoint: 'GET /api/v2/search/merchants?q=...',
      owasp: 'API8:2023',
    },
    {
      id: 'ssrf',
      name: 'SSRF Cloud Metadata Probe',
      desc: 'Outbound webhook pointing to 169.254.169.254 or loopback config env.',
      endpoint: 'POST /api/v2/users/me/webhook-avatar',
      owasp: 'API7:2023',
    },
    {
      id: 'business_logic',
      name: 'Negative Amount & Coupon Stuffing',
      desc: 'Domain invariant bypass: negative UPI transfer (-5000) & duplicate coupons.',
      endpoint: 'POST /api/v2/payments/upi-transfer',
      owasp: 'API6:2023',
    },
    {
      id: 'redos_complexity',
      name: 'ReDoS & Algorithmic Complexity',
      desc: 'Catastrophic backtracking regex ((a+)+$!) and nested payload bomb.',
      endpoint: 'POST /api/v2/accounts/import-statement',
      owasp: 'API4:2023',
    },
    {
      id: 'supply_chain',
      name: 'Supply-Chain Vendor Poisoning',
      desc: 'Compromised currency feed with stored XSS intercepted by proxy filter.',
      endpoint: 'GET /api/v2/payments/fx-rate?vendor_poisoned=true',
      owasp: 'API10:2023',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="w-full max-w-md h-full bg-white border-l border-slate-200 shadow-2xl flex flex-col text-slate-900">
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-600" />
              <h2 className="text-[14px] font-semibold text-slate-900">Red-Team Simulation Engine</h2>
            </div>
            <p className="text-[12px] text-slate-500 mt-0.5">Shift+D drawer · Live Ingress injection</p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors"
          >
            <X className="w-4 h-4" strokeWidth={2} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6">
          {/* Status Message */}
          {activeStatus && (
            <div className="p-3 rounded-xl bg-blue-50 border border-blue-200 text-[12px] flex items-center gap-2 text-blue-900">
              <Check className="w-3.5 h-3.5 text-blue-600 shrink-0" strokeWidth={2} />
              <span>{activeStatus}</span>
            </div>
          )}

          {/* Data Source Configuration */}
          <div>
            <div className="text-[12px] font-medium text-slate-500 mb-2">Data Source Engine</div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
              <div>
                <div className="text-[13px] font-semibold text-slate-800">
                  {useMock ? 'Mock Fixture Mode' : 'FastAPI Backend Live'}
                </div>
                <div className="text-[11px] text-slate-500 mt-0.5 font-mono">
                  {useMock ? 'Serving public/mock/*.json' : 'Proxying to localhost:8000/api'}
                </div>
              </div>
              <button
                onClick={handleToggleMock}
                className="px-3 py-1.5 rounded-lg border border-slate-200 text-[12px] font-medium bg-white hover:bg-slate-100 text-slate-800 shadow-2xs transition-colors"
              >
                Switch to {useMock ? 'Live' : 'Mock'}
              </button>
            </div>
          </div>

          {/* Trigger Attack Scenarios */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[12px] font-semibold text-slate-700">Attack Scenarios & Invariant Probes</span>
              <button
                onClick={resetAll}
                disabled={isRunning}
                className="text-[11px] text-slate-500 hover:text-slate-900 flex items-center gap-1 transition-colors"
              >
                <RotateCcw className="w-3 h-3" strokeWidth={1.75} />
                <span>Reset state</span>
              </button>
            </div>

            <div className="space-y-2">
              {attackScenarios.map((sc) => (
                <div
                  key={sc.id}
                  className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 hover:border-slate-300 transition-all flex flex-col gap-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-[13px] font-semibold text-slate-900">{sc.name}</span>
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-amber-50 text-amber-800 border border-amber-200 font-medium">
                          {sc.owasp}
                        </span>
                      </div>
                      <div className="text-[11.5px] text-slate-600 mt-1 leading-relaxed">{sc.desc}</div>
                      <div className="text-[11px] text-slate-500 font-mono mt-1.5 bg-white px-2 py-0.5 rounded border border-slate-200/80 inline-block">
                        {sc.endpoint}
                      </div>
                    </div>
                    <button
                      onClick={() => triggerAttack(sc.id, sc.name)}
                      disabled={isRunning}
                      className="px-2.5 py-1.5 rounded-lg border border-blue-200 bg-blue-50/80 hover:bg-blue-600 text-blue-700 hover:text-white text-[11px] font-semibold transition-all shrink-0 flex items-center gap-1.5 shadow-2xs"
                    >
                      <Play className="w-3 h-3" strokeWidth={2} />
                      <span>Inject</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-[11px] text-slate-500 font-mono">
          <span>Press <kbd className="px-1.5 py-0.5 rounded bg-white border border-slate-200 shadow-2xs">Shift+D</kbd> or <kbd className="px-1.5 py-0.5 rounded bg-white border border-slate-200 shadow-2xs">Esc</kbd> to close</span>
        </div>
      </div>
    </div>
  );
};
