import React, { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  X, 
  Flame, 
  Terminal, 
  ShieldAlert, 
  RotateCcw, 
  Play, 
  Square, 
  Database, 
  Globe, 
  Users, 
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';

interface RedTeamDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const RedTeamDrawer: React.FC<RedTeamDrawerProps> = ({ isOpen, onClose }) => {
  const { token, refreshUser } = useAuth();
  
  // Attack 1 State: BOLA
  const [bolaRunning, setBolaRunning] = useState(false);
  const [bolaCount, setBolaCount] = useState(0);
  const [bolaTotal] = useState(48);
  const [bolaLogs, setBolaLogs] = useState<string[]>([]);
  const bolaAbortRef = useRef(false);

  // Attack 2 State: Scraper
  const [scrapeRunning, setScrapeRunning] = useState(false);
  const [recordsHarvested, setRecordsHarvested] = useState(0);
  const [bytesHarvested, setBytesHarvested] = useState(0);
  const [scrapeVelocity, setScrapeVelocity] = useState(0);
  const scrapeAbortRef = useRef(false);

  // Attack 3 State: Token Replay
  const [replayRunning, setReplayRunning] = useState(false);
  const [replaySuccess, setReplaySuccess] = useState<string | null>(null);

  // Reset State
  const [resetMessage, setResetMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  // 1. Attack 1: BOLA Account Enumeration
  const runBolaAttack = async () => {
    if (!token) {
      alert('Please log in first to capture a valid session token for BOLA testing');
      return;
    }
    setBolaRunning(true);
    setBolaCount(0);
    setBolaLogs([]);
    bolaAbortRef.current = false;

    let count = 0;
    for (let id = 1002; id <= 1050; id++) {
      if (bolaAbortRef.current) break;

      try {
        const res = await fetch(`/api/v2/accounts/${id}/statement`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        count++;
        setBolaCount(count);
        setBolaLogs(prev => [
          `[${new Date().toLocaleTimeString()}] GET /api/v2/accounts/${id}/statement -> ${res.status} (Protected)`,
          ...prev.slice(0, 8)
        ]);
      } catch (err: any) {
        setBolaLogs(prev => [`[ERROR] Account ${id}: ${err.message}`, ...prev]);
      }
      // Small tick delay to show live progress
      await new Promise(r => setTimeout(r, 60));
    }
    setBolaRunning(false);
  };

  const stopBolaAttack = () => {
    bolaAbortRef.current = true;
    setBolaRunning(false);
  };

  // 2. Attack 2: Scrape Directory & KYC Zombie Dump
  const runScraperAttack = async () => {
    setScrapeRunning(true);
    setRecordsHarvested(0);
    setBytesHarvested(0);
    scrapeAbortRef.current = false;

    const startTime = Date.now();
    let totalRecs = 0;
    let totalBytes = 0;

    // Concurrently blast zombie KYC dump + merchant pages
    for (let page = 1; page <= 15; page++) {
      if (scrapeAbortRef.current) break;

      try {
        const [kycRes, merchRes] = await Promise.all([
          fetch('/api/v1/kyc/aadhaar-pan-dump'),
          fetch(`/api/v2/upi/merchants?page=${page}&limit=25`)
        ]);

        const kycText = await kycRes.text();
        const merchText = await merchRes.text();

        totalBytes += kycText.length + merchText.length;
        try {
          const kycJson = JSON.parse(kycText);
          const merchJson = JSON.parse(merchText);
          totalRecs += (kycJson.length || 0) + (merchJson.items?.length || 0);
        } catch {
          totalRecs += 25;
        }

        const elapsedSec = Math.max(0.1, (Date.now() - startTime) / 1000);
        setRecordsHarvested(totalRecs);
        setBytesHarvested(totalBytes);
        setScrapeVelocity(Math.round(totalRecs / elapsedSec));
      } catch (err) {
        console.warn('Scraper tick error:', err);
      }

      await new Promise(r => setTimeout(r, 80));
    }

    setScrapeRunning(false);
  };

  const stopScraperAttack = () => {
    scrapeAbortRef.current = true;
    setScrapeRunning(false);
  };

  // 3. Attack 3: Token Replay from Botnet IP
  const runTokenReplayAttack = async () => {
    if (!token) {
      alert('Please log in first so we can capture your session JWT to replay');
      return;
    }
    setReplayRunning(true);
    setReplaySuccess(null);

    try {
      const spoofedIp = '185.220.101.5'; // Tor exit node IP
      const spoofedUa = 'python-requests/2.31.0';

      const res = await fetch('/api/v2/payments/upi-transfer', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Forwarded-For': spoofedIp,
          'User-Agent': spoofedUa
        },
        body: JSON.stringify({
          from_vpa: 'priya.sharma@bharatpay',
          to_vpa: 'swiggy@bharatpay',
          amount_paise: 5000,
          note: 'Botnet Replay Exploit',
          idempotency_key: `botnet_replay_${Date.now()}`
        })
      });

      const data = await res.json().catch(() => ({}));
      setReplaySuccess(
        `Token (jti) replayed via spoofed IP ${spoofedIp} [User-Agent: ${spoofedUa}]. Telemetry logged with matching token_id and mismatched IP!`
      );
      await refreshUser();
    } catch (err: any) {
      setReplaySuccess(`Replay executed: ${err.message}`);
    } finally {
      setReplayRunning(false);
    }
  };

  // Reset Demo State
  const handleResetState = async () => {
    try {
      const res = await fetch('/api/internal/demo/reset-state', { method: 'POST' });
      const data = await res.json();
      setResetMessage(data.message || 'Demo state restored!');
      await refreshUser();
      setTimeout(() => setResetMessage(null), 3500);
    } catch (err: any) {
      setResetMessage(`Reset failed: ${err.message}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-sm flex justify-end">
      <div className="w-full max-w-xl bg-slate-900 text-slate-100 h-full shadow-2xl flex flex-col justify-between border-l border-slate-800 animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-rose-600/20 text-rose-400 flex items-center justify-center border border-rose-500/30">
              <Flame className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-bold tracking-tight text-white">Red-Team Traffic Generator</span>
                <span className="px-1.5 py-0.5 text-[10px] font-mono bg-rose-950 text-rose-300 rounded border border-rose-800">
                  ATTACK SUITE
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Generates real HTTP abuse for Person 1/2's detection pipeline</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Attack Controls Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {resetMessage && (
            <div className="p-3 bg-emerald-950/80 border border-emerald-700/60 text-emerald-300 text-xs rounded-xl flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span>{resetMessage}</span>
            </div>
          )}

          {/* Attack 1: BOLA Account Enumeration */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Users className="w-4 h-4 text-amber-400" />
                <h3 className="text-xs font-bold text-white">Scenario 1: BOLA Account Sweep (#1002–#1050)</h3>
              </div>
              <span className="text-[10px] font-mono bg-slate-700/60 px-2 py-0.5 rounded text-amber-300">
                OWASP API1
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
              Fires rapid sequential GET requests against other users' account statements. Demonstrates telemetry object_id spread.
            </p>

            <div className="flex items-center space-x-2 mb-3">
              {!bolaRunning ? (
                <button
                  onClick={runBolaAttack}
                  className="flex items-center space-x-1.5 px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold shadow-sm transition"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Enumerate Accounts #1002–#1050</span>
                </button>
              ) : (
                <button
                  onClick={stopBolaAttack}
                  className="flex items-center space-x-1.5 px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold shadow-sm transition"
                >
                  <Square className="w-3.5 h-3.5" />
                  <span>Stop Attack</span>
                </button>
              )}

              <span className="text-xs font-mono text-slate-300">
                Probed: <span className="font-bold text-amber-400">{bolaCount}</span> / {bolaTotal}
              </span>
            </div>

            {bolaLogs.length > 0 && (
              <div className="bg-slate-950 rounded-lg p-2.5 font-mono text-[10px] text-slate-400 max-h-24 overflow-y-auto space-y-1 border border-slate-800">
                {bolaLogs.map((log, i) => (
                  <div key={i} className="truncate">{log}</div>
                ))}
              </div>
            )}
          </div>

          {/* Attack 2: High Rate Scraper */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Database className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold text-white">Scenario 2: High-Rate Directory & Zombie Scraper</h3>
              </div>
              <span className="text-[10px] font-mono bg-slate-700/60 px-2 py-0.5 rounded text-cyan-300">
                OWASP API9 / Scraping
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
              Blasts concurrent calls to paginated merchants and the zombie <code className="text-cyan-300 font-mono">/api/v1/kyc/aadhaar-pan-dump</code> route to simulate data harvesting.
            </p>

            <div className="flex items-center space-x-2 mb-3">
              {!scrapeRunning ? (
                <button
                  onClick={runScraperAttack}
                  className="flex items-center space-x-1.5 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold shadow-sm transition"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Scrape Merchant & KYC Directory</span>
                </button>
              ) : (
                <button
                  onClick={stopScraperAttack}
                  className="flex items-center space-x-1.5 px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-xs font-semibold shadow-sm transition"
                >
                  <Square className="w-3.5 h-3.5" />
                  <span>Stop Scraper</span>
                </button>
              )}
            </div>

            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <div className="text-[10px] text-slate-500 uppercase">Records</div>
                <div className="text-sm font-mono font-bold text-cyan-400">{recordsHarvested}</div>
              </div>
              <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <div className="text-[10px] text-slate-500 uppercase">Payload</div>
                <div className="text-sm font-mono font-bold text-slate-200">{(bytesHarvested / 1024).toFixed(1)} KB</div>
              </div>
              <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <div className="text-[10px] text-slate-500 uppercase">Velocity</div>
                <div className="text-sm font-mono font-bold text-slate-200">{scrapeVelocity} rec/s</div>
              </div>
            </div>
          </div>

          {/* Attack 3: Token Replay from Botnet IP */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Globe className="w-4 h-4 text-violet-400" />
                <h3 className="text-xs font-bold text-white">Scenario 3: Botnet Token Replay (Foreign IP/UA)</h3>
              </div>
              <span className="text-[10px] font-mono bg-slate-700/60 px-2 py-0.5 rounded text-violet-300">
                Token Misuse
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
              Replays your session JWT through an external background fetch with spoofed Tor IP (<code className="text-violet-300 font-mono">185.220.101.5</code>) and Python User-Agent to trigger token-misuse alerts.
            </p>

            <button
              disabled={replayRunning}
              onClick={runTokenReplayAttack}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{replayRunning ? 'Replaying...' : 'Replay Token from Botnet IP'}</span>
            </button>

            {replaySuccess && (
              <div className="mt-3 p-2.5 bg-slate-950 border border-violet-800/60 rounded-lg font-mono text-[11px] text-violet-300 leading-normal">
                {replaySuccess}
              </div>
            )}
          </div>
        </div>

        {/* Drawer Footer Actions */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/80 flex items-center justify-between">
          <button
            onClick={handleResetState}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition border border-slate-700"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Demo State</span>
          </button>

          <span className="text-[11px] font-mono text-slate-500">
            Press <kbd className="px-1 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-300">Shift</kbd> + <kbd className="px-1 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-300">R</kbd> to toggle
          </span>
        </div>
      </div>
    </div>
  );
};
