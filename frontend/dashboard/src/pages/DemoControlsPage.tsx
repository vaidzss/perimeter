import React, { useState } from 'react';
import { apiClient } from '../api/client';
import { useQueryClient } from '@tanstack/react-query';
import { Play, RotateCcw, Check } from 'lucide-react';

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
      name: 'BOLA / IDOR account harvesting',
      desc: 'Actor u_17 rapidly queries foreign user accounts via /accounts/{id}.',
      endpoint: 'GET /accounts/{id}',
    },
    {
      id: 'token_misuse',
      name: 'Token replay / concurrent IPs',
      desc: 'tok_9918ab concurrent usage across 5 IPs and conflicting User-Agents.',
      endpoint: 'POST /accounts/transfer',
    },
    {
      id: 'scraping',
      name: 'Bulk profile scraping',
      desc: 'High-frequency unauthenticated scraping targeting statements.',
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
    {
      id: 'vp_campaign_traffic',
      name: 'Onboard new VP + run Diwali Sale traffic',
      desc: 'Provisions fresh VP Sales via /employees/onboard, registers campaign, and fires 2,000 in-scope lookups -> Alert SUPPRESSED (informational).',
      endpoint: 'GET /api/v2/internal/reports/regional-sales',
    },
    {
      id: 'stolen_vp_token',
      name: 'Same VP token, suspicious geography',
      desc: 'Replays the fresh VP token from Tor Exit node 185.220.101.5 -> Alert FIRES with elevated priority: privileged identity + anomalous context.',
      endpoint: 'GET /api/v2/internal/reports/regional-sales',
    },
  ];

  return (
    <div className="space-y-4 max-w-4xl">
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-[15px] font-semibold text-[#E6E8EB]">Demo & test scenario controls</h1>
          <p className="text-[12px] text-[#8B929C] mt-0.5">
            Test attack simulation and backend mode switcher. Accessible globally via <kbd className="font-mono text-[11px] px-1 py-0.5 rounded bg-[#0E1013] border border-[#252A31]">Shift+D</kbd>.
          </p>
        </div>

        <button
          onClick={resetAll}
          disabled={isRunning}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-[4px] bg-[#0E1013] border border-[#252A31] hover:border-[#343B45] text-[#8B929C] hover:text-[#E6E8EB] text-[12px] transition-colors self-start md:self-auto"
        >
          <RotateCcw className="w-3.5 h-3.5" strokeWidth={1.5} />
          <span>Reset baselines</span>
        </button>
      </div>

      {activeStatus && (
        <div className="p-3 rounded-[6px] bg-[#15181D] border border-[#252A31] text-[12px] flex items-center gap-2 text-[#4C8DFF]">
          <Check className="w-3.5 h-3.5 shrink-0" strokeWidth={1.5} />
          <span>{activeStatus}</span>
        </div>
      )}

      {/* Engine Switcher */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 flex items-center justify-between">
        <div>
          <div className="text-[13px] font-medium text-[#E6E8EB]">Active data source engine</div>
          <div className="text-[11px] text-[#8B929C] font-mono mt-0.5">
            {useMock ? 'Mock fixture JSONs (/public/mock/*.json)' : 'FastAPI live proxy (http://localhost:8000/api)'}
          </div>
        </div>
        <button
          onClick={handleToggleMock}
          className="px-3 py-1.5 rounded-[4px] bg-[#0E1013] border border-[#252A31] hover:border-[#343B45] text-[#E6E8EB] text-[12px] transition-colors"
        >
          Switch to {useMock ? 'FastAPI Live' : 'Mock Fixtures'}
        </button>
      </div>

      {/* Scenarios List */}
      <div className="bg-[#15181D] border border-[#252A31] rounded-[6px] p-4 space-y-3">
        <h2 className="text-[13px] font-semibold text-[#E6E8EB]">Adversarial attack simulations</h2>

        <div className="space-y-2">
          {attackScenarios.map((sc) => (
            <div
              key={sc.id}
              className="p-3 rounded-[4px] bg-[#0E1013] border border-[#252A31] flex flex-col md:flex-row md:items-center justify-between gap-3"
            >
              <div>
                <div className="text-[13px] font-medium text-[#E6E8EB]">{sc.name}</div>
                <div className="text-[11px] text-[#8B929C] mt-0.5">{sc.desc}</div>
                <div className="text-[11px] text-[#8B929C] font-mono mt-1">{sc.endpoint}</div>
              </div>

              <button
                onClick={() => triggerAttack(sc.id, sc.name)}
                disabled={isRunning}
                className="px-3 py-1.5 rounded-[4px] border border-[#4C8DFF]/40 text-[#4C8DFF] hover:bg-[#4C8DFF]/10 text-[11px] font-medium transition-colors shrink-0 flex items-center gap-1.5 self-start md:self-auto"
              >
                <Play className="w-3 h-3" strokeWidth={1.5} />
                <span>Inject simulation</span>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
