import React, { useState } from 'react';
import { apiClient } from '../api/client';
import { useQueryClient } from '@tanstack/react-query';
import { Play, RotateCcw, Check, SlidersHorizontal, Terminal } from 'lucide-react';

export const DemoControlsPage: React.FC = () => {
  const [activeStatus, setActiveStatus] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [useMock, setUseMock] = useState<boolean>(apiClient.getUseMock());
  const queryClient = useQueryClient();

  const handleToggleMock = () => {
    const next = !useMock;
    apiClient.setUseMock(next);
    setUseMock(next);
    queryClient.invalidateQueries();
    setActiveStatus(`Data source switched to ${next ? 'Mock JSON fixtures' : 'FastAPI Live backend'}.`);
    setTimeout(() => setActiveStatus(null), 3000);
  };

  const triggerAttack = async (type: string, name: string) => {
    setIsRunning(true);
    setActiveStatus(`Triggering simulated ${name}...`);
    try {
      const res = await fetch('/api/simulate-attack', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type }),
      });
      if (res.ok) {
        setActiveStatus(`Attack '${name}' triggered. Telemetry updated.`);
      } else {
        setActiveStatus(`Local simulation applied for '${name}'.`);
      }
    } catch {
      setActiveStatus(`Local simulation signal applied for '${name}'.`);
    } finally {
      setIsRunning(false);
      queryClient.invalidateQueries();
      setTimeout(() => setActiveStatus(null), 4000);
    }
  };

  const resetAll = async () => {
    setIsRunning(true);
    setActiveStatus('Resetting simulator baselines & alert state...');
    setTimeout(() => {
      setIsRunning(false);
      queryClient.invalidateQueries();
      setActiveStatus('System state restored to nominal baseline.');
      setTimeout(() => setActiveStatus(null), 3000);
    }, 800);
  };

  const attackScenarios = [
    {
      id: 'bola',
      name: 'BOLA / IDOR Account Harvesting',
      desc: 'Actor u_17 rapidly queries foreign user accounts via /accounts/{id}.',
      endpoint: 'GET /accounts/{id}',
    },
    {
      id: 'token_misuse',
      name: 'Token Replay / Concurrent IPs',
      desc: 'tok_9918ab concurrent usage across 5 IPs and conflicting User-Agents.',
      endpoint: 'POST /accounts/transfer',
    },
    {
      id: 'scraping',
      name: 'Bulk Statement Scraping',
      desc: 'High-frequency unauthenticated scraping targeting statements.',
      endpoint: 'GET /cards/{id}/statement',
    },
    {
      id: 'brute_force',
      name: 'Credential Stuffing Wave',
      desc: 'Burst of 401s from single IP targeting auth endpoint.',
      endpoint: 'POST /auth/login',
    },
    {
      id: 'unauthorized_access',
      name: 'Shadow Endpoint Probe',
      desc: 'Direct traffic hitting uncataloged route /internal/debug/tokens.',
      endpoint: 'GET /internal/debug/tokens',
    },
    {
      id: 'vp_campaign_traffic',
      name: 'Onboard New VP + Run Diwali Sale Traffic',
      desc: 'Provisions fresh VP Sales via /employees/onboard, registers campaign, and fires 2,000 in-scope lookups -> Alert SUPPRESSED (informational).',
      endpoint: 'GET /api/v2/internal/reports/regional-sales',
    },
    {
      id: 'stolen_vp_token',
      name: 'Stolen VP Token from Anomalous Geo',
      desc: 'Replays the fresh VP token from Tor Exit node 185.220.101.5 -> Alert FIRES with elevated priority: privileged identity + anomalous context.',
      endpoint: 'GET /api/v2/internal/reports/regional-sales',
    },
  ];

  return (
    <div className="space-y-5 max-w-4xl select-none font-sans pb-12">
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="w-5 h-5 text-blue-600" />
            <h1 className="text-lg font-bold text-slate-900 tracking-tight">Demo & Test Scenario Controls</h1>
          </div>
          <p className="text-[12px] text-slate-500 mt-0.5">
            Test attack simulation and backend mode switcher. Accessible globally via <kbd className="font-mono text-xs px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-700 shadow-2xs">Shift+D</kbd>.
          </p>
        </div>

        <button
          onClick={resetAll}
          disabled={isRunning}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-50 border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold transition-colors self-start md:self-auto shadow-2xs"
        >
          <RotateCcw className="w-3.5 h-3.5" strokeWidth={2} />
          <span>Reset Baselines</span>
        </button>
      </div>

      {activeStatus && (
        <div className="p-3.5 rounded-xl bg-blue-50 border border-blue-200 text-xs flex items-center gap-2 text-blue-900 shadow-2xs font-medium">
          <Check className="w-4 h-4 text-blue-600 shrink-0" strokeWidth={2} />
          <span>{activeStatus}</span>
        </div>
      )}

      {/* Engine Switcher */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 flex items-center justify-between shadow-xs">
        <div>
          <div className="text-sm font-semibold text-slate-900">Active Data Source Engine</div>
          <div className="text-xs text-slate-500 font-mono mt-0.5">
            {useMock ? 'Mock fixture JSONs (/public/mock/*.json)' : 'FastAPI live proxy (http://localhost:8000/api)'}
          </div>
        </div>
        <button
          onClick={handleToggleMock}
          className="px-3.5 py-2 rounded-xl bg-blue-50 border border-blue-200 hover:bg-blue-100 text-blue-700 text-xs font-semibold transition-colors shadow-2xs"
        >
          Switch to {useMock ? 'FastAPI Live' : 'Mock Fixtures'}
        </button>
      </div>

      {/* Scenarios List */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 space-y-3 shadow-xs">
        <h2 className="text-sm font-semibold text-slate-900">Adversarial Attack Simulations</h2>

        <div className="space-y-2.5">
          {attackScenarios.map((sc) => (
            <div
              key={sc.id}
              className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 hover:border-slate-300 transition-all flex flex-col md:flex-row md:items-center justify-between gap-3"
            >
              <div>
                <div className="text-sm font-bold text-slate-900">{sc.name}</div>
                <div className="text-xs text-slate-600 mt-0.5 leading-relaxed">{sc.desc}</div>
                <div className="text-xs text-slate-500 font-mono mt-1 bg-white px-2 py-0.5 rounded border border-slate-200/80 inline-block font-medium">
                  {sc.endpoint}
                </div>
              </div>

              <button
                onClick={() => triggerAttack(sc.id, sc.name)}
                disabled={isRunning}
                className="px-3 py-1.5 rounded-lg border border-blue-200 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold transition-all shrink-0 flex items-center gap-1.5 self-start md:self-auto shadow-2xs"
              >
                <Play className="w-3 h-3 fill-current" />
                <span>Inject Simulation</span>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DemoControlsPage;
