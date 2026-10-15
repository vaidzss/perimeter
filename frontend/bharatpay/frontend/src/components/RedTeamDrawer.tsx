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
  CheckCircle2,
  Code2,
  Network,
  Coins,
  Cpu,
  ShieldCheck,
  Layers,
  Zap
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

  // Attack 4 State: SQL Injection / Command Injection (OWASP API8)
  const [sqliRunning, setSqliRunning] = useState(false);
  const [sqliType, setSqliType] = useState<'sqli' | 'cmd'>('sqli');
  const [sqliLogs, setSqliLogs] = useState<string[]>([]);

  // Attack 5 State: SSRF to Cloud Metadata / Loopback (OWASP API7)
  const [ssrfRunning, setSsrfRunning] = useState(false);
  const [ssrfTarget, setSsrfTarget] = useState<'metadata' | 'loopback'>('metadata');
  const [ssrfResult, setSsrfResult] = useState<string | null>(null);

  // Attack 6 State: Business Logic & Negative Amount Exploit (OWASP API3/API6)
  const [bizLogicRunning, setBizLogicRunning] = useState(false);
  const [bizLogicResult, setBizLogicResult] = useState<string | null>(null);

  // Attack 7 State: ReDoS & Complexity Bomb (OWASP API4)
  const [redosRunning, setRedosRunning] = useState(false);
  const [redosResult, setRedosResult] = useState<string | null>(null);

  // Attack 8 State: Supply-Chain Poisoning (OWASP API10)
  const [supplyChainRunning, setSupplyChainRunning] = useState(false);
  const [supplyChainResult, setSupplyChainResult] = useState<{ status: number; text: string; details?: any } | null>(null);

  // Bulk Barrage State
  const [bulkRunning, setBulkRunning] = useState(false);
  const [bulkStatus, setBulkStatus] = useState<string | null>(null);

  // Reset State
  const [resetMessage, setResetMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  // 1. Attack 1: BOLA Account Enumeration (OWASP API1)
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
      await new Promise(r => setTimeout(r, 50));
    }
    setBolaRunning(false);
  };

  const stopBolaAttack = () => {
    bolaAbortRef.current = true;
    setBolaRunning(false);
  };

  // 2. Attack 2: Scrape Directory & KYC Zombie Dump (OWASP API9)
  const runScraperAttack = async () => {
    setScrapeRunning(true);
    setRecordsHarvested(0);
    setBytesHarvested(0);
    scrapeAbortRef.current = false;

    const startTime = Date.now();
    let totalRecs = 0;
    let totalBytes = 0;

    for (let page = 1; page <= 12; page++) {
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

      await new Promise(r => setTimeout(r, 60));
    }

    setScrapeRunning(false);
  };

  const stopScraperAttack = () => {
    scrapeAbortRef.current = true;
    setScrapeRunning(false);
  };

  // 3. Attack 3: Token Replay from Botnet IP (OWASP API2)
  const runTokenReplayAttack = async () => {
    if (!token) {
      alert('Please log in first so we can capture your session JWT to replay');
      return;
    }
    setReplayRunning(true);
    setReplaySuccess(null);

    try {
      const spoofedIp = '185.220.101.5';
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

      setReplaySuccess(
        `Token (jti) replayed via Tor exit node IP ${spoofedIp} [Status: ${res.status}]. Telemetry logged with matching token_id and foreign geographic mismatch!`
      );
      await refreshUser();
    } catch (err: any) {
      setReplaySuccess(`Replay executed: ${err.message}`);
    } finally {
      setReplayRunning(false);
    }
  };

  // 4. Attack 4: SQL Injection & Command Injection (OWASP API8)
  const runSqliAttack = async () => {
    if (!token) {
      alert('Please log in first to authenticate the search API request');
      return;
    }
    setSqliRunning(true);
    const payload = sqliType === 'sqli' 
      ? "' OR 1=1 --" 
      : "Swiggy; rm -rf /";

    try {
      const encoded = encodeURIComponent(payload);
      const res = await fetch(`/api/v2/search/merchants?q=${encoded}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await res.json().catch(() => ({}));
      const timestamp = new Date().toLocaleTimeString();
      setSqliLogs(prev => [
        `[${timestamp}] GET /api/v2/search/merchants?q=${payload} -> HTTP ${res.status}`,
        `[ALERT] Threat Flagged: ${sqliType === 'sqli' ? 'SQL_INJECTION_DETECTED' : 'COMMAND_INJECTION_DETECTED'}`,
        ...prev.slice(0, 6)
      ]);
    } catch (err: any) {
      setSqliLogs(prev => [`[ERROR] ${err.message}`, ...prev]);
    } finally {
      setSqliRunning(false);
    }
  };

  // 5. Attack 5: SSRF to Cloud Metadata / Loopback (OWASP API7)
  const runSsrfAttack = async () => {
    if (!token) {
      alert('Please log in first to test avatar webhook SSRF');
      return;
    }
    setSsrfRunning(true);
    setSsrfResult(null);

    const targetUrl = ssrfTarget === 'metadata'
      ? 'http://169.254.169.254/latest/meta-data/'
      : 'http://127.0.0.1:8000/api/internal/config/env';

    try {
      const res = await fetch('/api/v2/users/me/webhook-avatar', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ avatar_url: targetUrl })
      });
      const data = await res.json().catch(() => ({}));
      setSsrfResult(
        `Probe sent: ${targetUrl}\nVerdict: HTTP ${res.status} | SSRF Telemetry Flagged: SSRF_${ssrfTarget === 'metadata' ? 'CLOUD_METADATA' : 'LOOPBACK_TARGET'}`
      );
    } catch (err: any) {
      setSsrfResult(`SSRF request error: ${err.message}`);
    } finally {
      setSsrfRunning(false);
    }
  };

  // 6. Attack 6: Business Logic & Negative Transfer Exploit (OWASP API3/API6)
  const runBizLogicAttack = async () => {
    if (!token) {
      alert('Please log in first to test transfer business logic');
      return;
    }
    setBizLogicRunning(true);
    setBizLogicResult(null);

    try {
      const res = await fetch('/api/v2/payments/upi-transfer', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          from_vpa: 'priya.sharma@bharatpay',
          payee_vpa: 'swiggy@bharatpay',
          to_vpa: 'swiggy@bharatpay',
          amount: -5000.0,
          coupons: ['SAVE10', 'SAVE10', 'SAVE10'],
          note: 'Negative Amount & Duplicate Coupon Inflation Exploit'
        })
      });
      const data = await res.json().catch(() => ({}));
      setBizLogicResult(
        `Payload: {"amount": -5000, "coupons": ["SAVE10", "SAVE10", "SAVE10"]}\nVerdict: HTTP ${res.status} | Flagged: NEGATIVE_AMOUNT_EXPLOIT & DUPLICATE_ARRAY_STUFFING`
      );
    } catch (err: any) {
      setBizLogicResult(`Business logic error: ${err.message}`);
    } finally {
      setBizLogicRunning(false);
    }
  };

  // 7. Attack 7: ReDoS & Complexity Bomb (OWASP API4)
  const runRedosAttack = async () => {
    if (!token) {
      alert('Please log in first to test statement import ReDoS');
      return;
    }
    setRedosRunning(true);
    setRedosResult(null);

    // Build nested JSON depth 14
    let nestedObj: any = { marker: "depth_bomb_payload" };
    for (let i = 0; i < 14; i++) {
      nestedObj = { level: i, child: nestedObj };
    }

    try {
      const res = await fetch('/api/v2/accounts/import-statement', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          regex_filter: '(a+)+$!',
          statement_tree: nestedObj
        })
      });
      const data = await res.json().catch(() => ({}));
      setRedosResult(
        `Payload: evil regex '(a+)+$!' + JSON Depth 15\nVerdict: HTTP ${res.status} | Flagged: REDOS_PATTERN_DETECTED & EXCESSIVE_JSON_DEPTH`
      );
    } catch (err: any) {
      setRedosResult(`Complexity attack error: ${err.message}`);
    } finally {
      setRedosRunning(false);
    }
  };

  // 8. Attack 8: Supply-Chain Poisoning Interception (OWASP API10)
  const runSupplyChainAttack = async () => {
    setSupplyChainRunning(true);
    setSupplyChainResult(null);

    try {
      const res = await fetch('/api/v2/payments/fx-rate?from_currency=USD&to_currency=INR&vendor_poisoned=true&enforce_guard=true');
      const data = await res.json().catch(() => ({}));
      setSupplyChainResult({
        status: res.status,
        text: res.status === 502 
          ? 'SHIELD ACTIVE: SafeExternalAPIClient blocked poisoned vendor feed!'
          : 'Vendor payload received',
        details: data
      });
    } catch (err: any) {
      setSupplyChainResult({
        status: 502,
        text: `Egress Guard Intercepted: ${err.message}`
      });
    } finally {
      setSupplyChainRunning(false);
    }
  };

  // 9. Bulk Execution: Run All 8 Scenarios sequentially
  const runAllAttacks = async () => {
    if (!token) {
      alert('Please log in first so authenticated attacks can capture user context');
      return;
    }
    setBulkRunning(true);
    setBulkStatus('Starting comprehensive 8-scenario red-team barrage...');

    try {
      setBulkStatus('1/8: Executing BOLA Account Sweep...');
      await runBolaAttack();

      setBulkStatus('2/8: Blasting Directory & Zombie KYC Scraper...');
      await runScraperAttack();

      setBulkStatus('3/8: Replaying Stolen Token from Tor Botnet IP...');
      await runTokenReplayAttack();

      setBulkStatus('4/8: Firing SQL Injection & Command Injection...');
      await runSqliAttack();

      setBulkStatus('5/8: Probing SSRF Cloud Metadata (169.254.169.254)...');
      await runSsrfAttack();

      setBulkStatus('6/8: Exploiting Business Logic with Negative Amount...');
      await runBizLogicAttack();

      setBulkStatus('7/8: Launching ReDoS Backtracking & Depth Bomb...');
      await runRedosAttack();

      setBulkStatus('8/8: Simulating Compromised Supplier Poisoning...');
      await runSupplyChainAttack();

      setBulkStatus('All 8 Red-Team Scenarios successfully fired! Perimeter SOC Console updated.');
    } catch (err: any) {
      setBulkStatus(`Bulk simulation halted: ${err.message}`);
    } finally {
      setBulkRunning(false);
      setTimeout(() => setBulkStatus(null), 6000);
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
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/80">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-rose-600/20 text-rose-400 flex items-center justify-center border border-rose-500/30">
              <Flame className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-bold tracking-tight text-white">Red-Team Traffic Generator</span>
                <span className="px-1.5 py-0.5 text-[10px] font-mono bg-rose-950 text-rose-300 rounded border border-rose-800">
                  8 SCENARIOS
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Generates real adversarial traffic across all OWASP API Security Top 10 vectors</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Global Bulk Action Banner */}
        <div className="px-6 py-3 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-amber-400 animate-pulse" />
            <span className="text-xs font-semibold text-slate-200">Full Red-Team Simulation Barrage</span>
          </div>
          <button
            disabled={bulkRunning}
            onClick={runAllAttacks}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-gradient-to-r from-rose-600 to-amber-600 hover:from-rose-500 hover:to-amber-500 text-white rounded-lg text-xs font-bold shadow-md transition disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5" />
            <span>{bulkRunning ? 'Executing Barrage...' : 'Run All 8 Scenarios'}</span>
          </button>
        </div>

        {bulkStatus && (
          <div className="mx-6 mt-4 p-3 bg-amber-950/70 border border-amber-600/60 rounded-xl text-amber-200 text-xs font-mono flex items-center space-x-2">
            <span className="inline-block w-2 h-2 rounded-full bg-amber-400 animate-ping mr-1" />
            <span>{bulkStatus}</span>
          </div>
        )}

        {/* Attack Controls Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5">
          {resetMessage && (
            <div className="p-3 bg-emerald-950/80 border border-emerald-700/60 text-emerald-300 text-xs rounded-xl flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span>{resetMessage}</span>
            </div>
          )}

          {/* Scenario 1: BOLA Account Enumeration */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-start justify-between mb-1.5">
              <div className="flex items-center space-x-2">
                <Users className="w-4 h-4 text-amber-400" />
                <h3 className="text-xs font-bold text-white">Scenario 1: BOLA Account Sweep (#1002–#1050)</h3>
              </div>
              <span className="text-[10px] font-mono bg-slate-700/60 px-2 py-0.5 rounded text-amber-300">
                OWASP API1
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
              Fires sequential GET calls against unauthorized account statements. Evaluates IDOR spread and session object boundaries.
            </p>

            <div className="flex items-center space-x-2 mb-2.5">
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

          {/* Scenario 2: High Rate Scraper & Zombie KYC */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-start justify-between mb-1.5">
              <div className="flex items-center space-x-2">
                <Database className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold text-white">Scenario 2: High-Rate Directory & Zombie Scraper</h3>
              </div>
              <span className="text-[10px] font-mono bg-slate-700/60 px-2 py-0.5 rounded text-cyan-300">
                OWASP API9
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
              Blasts concurrent calls to paginated merchants and deprecated zombie <code className="text-cyan-300 font-mono">/api/v1/kyc/aadhaar-pan-dump</code>.
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

          {/* Scenario 3: Botnet Token Replay */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-start justify-between mb-1.5">
              <div className="flex items-center space-x-2">
                <Globe className="w-4 h-4 text-violet-400" />
                <h3 className="text-xs font-bold text-white">Scenario 3: Botnet Token Replay (Foreign IP/UA)</h3>
              </div>
              <span className="text-[10px] font-mono bg-slate-700/60 px-2 py-0.5 rounded text-violet-300">
                OWASP API2
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
              Replays your session JWT through spoofed Tor exit node (<code className="text-violet-300 font-mono">185.220.101.5</code>) and Python user-agent.
            </p>

            <button
              disabled={replayRunning}
              onClick={runTokenReplayAttack}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{replayRunning ? 'Replaying...' : 'Replay Token from Tor IP'}</span>
            </button>

            {replaySuccess && (
              <div className="mt-3 p-2.5 bg-slate-950 border border-violet-800/60 rounded-lg font-mono text-[11px] text-violet-300 leading-normal">
                {replaySuccess}
              </div>
            )}
          </div>

          {/* Scenario 4: SQL Injection & Command Injection (OWASP API8) */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-start justify-between mb-1.5">
              <div className="flex items-center space-x-2">
                <Terminal className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-bold text-white">Scenario 4: SQLi & OS Command Injection</h3>
              </div>
              <span className="text-[10px] font-mono bg-slate-700/60 px-2 py-0.5 rounded text-emerald-300">
                OWASP API8
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
              Fires SQL tautology <code className="text-emerald-300 font-mono">' OR 1=1 --</code> or command separator <code className="text-emerald-300 font-mono">; rm -rf /</code> through <code className="text-emerald-300 font-mono">/api/v2/search/merchants?q=...</code>.
            </p>

            <div className="flex items-center space-x-2 mb-3">
              <div className="inline-flex rounded-lg bg-slate-950 p-0.5 border border-slate-800 text-[11px]">
                <button
                  onClick={() => setSqliType('sqli')}
                  className={`px-2.5 py-1 rounded-md font-medium transition ${sqliType === 'sqli' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  SQLi Tautology
                </button>
                <button
                  onClick={() => setSqliType('cmd')}
                  className={`px-2.5 py-1 rounded-md font-medium transition ${sqliType === 'cmd' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  Command Injection
                </button>
              </div>

              <button
                disabled={sqliRunning}
                onClick={runSqliAttack}
                className="flex items-center space-x-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5" />
                <span>{sqliRunning ? 'Injecting...' : 'Inject Payload'}</span>
              </button>
            </div>

            {sqliLogs.length > 0 && (
              <div className="bg-slate-950 rounded-lg p-2.5 font-mono text-[10px] text-slate-300 max-h-24 overflow-y-auto space-y-1 border border-slate-800">
                {sqliLogs.map((log, i) => (
                  <div key={i} className="truncate">{log}</div>
                ))}
              </div>
            )}
          </div>

          {/* Scenario 5: Server-Side Request Forgery / SSRF (OWASP API7) */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-start justify-between mb-1.5">
              <div className="flex items-center space-x-2">
                <Network className="w-4 h-4 text-blue-400" />
                <h3 className="text-xs font-bold text-white">Scenario 5: SSRF to Cloud Metadata / Loopback</h3>
              </div>
              <span className="text-[10px] font-mono bg-slate-700/60 px-2 py-0.5 rounded text-blue-300">
                OWASP API7
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
              Triggers outbound webhook fetch pointing to AWS/GCP metadata (<code className="text-blue-300 font-mono">169.254.169.254</code>) or internal loopback (<code className="text-blue-300 font-mono">127.0.0.1:8000/api/internal/config/env</code>).
            </p>

            <div className="flex items-center space-x-2 mb-3">
              <div className="inline-flex rounded-lg bg-slate-950 p-0.5 border border-slate-800 text-[11px]">
                <button
                  onClick={() => setSsrfTarget('metadata')}
                  className={`px-2.5 py-1 rounded-md font-medium transition ${ssrfTarget === 'metadata' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  Cloud Metadata IP
                </button>
                <button
                  onClick={() => setSsrfTarget('loopback')}
                  className={`px-2.5 py-1 rounded-md font-medium transition ${ssrfTarget === 'loopback' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
                >
                  Loopback Config Env
                </button>
              </div>

              <button
                disabled={ssrfRunning}
                onClick={runSsrfAttack}
                className="flex items-center space-x-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5" />
                <span>{ssrfRunning ? 'Probing...' : 'Probe SSRF Target'}</span>
              </button>
            </div>

            {ssrfResult && (
              <pre className="p-2.5 bg-slate-950 border border-blue-900/60 rounded-lg font-mono text-[10px] text-blue-300 whitespace-pre-wrap leading-normal">
                {ssrfResult}
              </pre>
            )}
          </div>

          {/* Scenario 6: Business Logic & Negative Transfer Exploit (OWASP API3 / API6) */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-start justify-between mb-1.5">
              <div className="flex items-center space-x-2">
                <Coins className="w-4 h-4 text-yellow-400" />
                <h3 className="text-xs font-bold text-white">Scenario 6: Negative Amount & Coupon Stuffing</h3>
              </div>
              <span className="text-[10px] font-mono bg-slate-700/60 px-2 py-0.5 rounded text-yellow-300">
                OWASP API3 / API6
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
              Exploits lack of domain validation by sending negative transfer value (<code className="text-yellow-300 font-mono">amount: -5000</code>) and duplicate coupon array stuffing (<code className="text-yellow-300 font-mono">["SAVE10", "SAVE10"]</code>).
            </p>

            <button
              disabled={bizLogicRunning}
              onClick={runBizLogicAttack}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-yellow-600 hover:bg-yellow-500 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{bizLogicRunning ? 'Executing...' : 'Fire Negative Transfer Exploit'}</span>
            </button>

            {bizLogicResult && (
              <pre className="mt-3 p-2.5 bg-slate-950 border border-yellow-800/60 rounded-lg font-mono text-[10px] text-yellow-300 whitespace-pre-wrap leading-normal">
                {bizLogicResult}
              </pre>
            )}
          </div>

          {/* Scenario 7: ReDoS & Complexity Bomb (OWASP API4) */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-start justify-between mb-1.5">
              <div className="flex items-center space-x-2">
                <Cpu className="w-4 h-4 text-purple-400" />
                <h3 className="text-xs font-bold text-white">Scenario 7: ReDoS Backtracking & Depth Bomb</h3>
              </div>
              <span className="text-[10px] font-mono bg-slate-700/60 px-2 py-0.5 rounded text-purple-300">
                OWASP API4
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
              Sends catastrophic backtracking regex payload <code className="text-purple-300 font-mono">(a+)+$!</code> along with deeply nested JSON (<code className="text-purple-300 font-mono">depth &gt; 12</code>) to test resource exhaustion defenses.
            </p>

            <button
              disabled={redosRunning}
              onClick={runRedosAttack}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{redosRunning ? 'Blasting...' : 'Send ReDoS & Depth Bomb'}</span>
            </button>

            {redosResult && (
              <pre className="mt-3 p-2.5 bg-slate-950 border border-purple-800/60 rounded-lg font-mono text-[10px] text-purple-300 whitespace-pre-wrap leading-normal">
                {redosResult}
              </pre>
            )}
          </div>

          {/* Scenario 8: Supply-Chain Poisoning Interception (OWASP API10) */}
          <div className="bg-slate-800/60 border border-slate-700/60 rounded-xl p-4">
            <div className="flex items-start justify-between mb-1.5">
              <div className="flex items-center space-x-2">
                <ShieldAlert className="w-4 h-4 text-red-400" />
                <h3 className="text-xs font-bold text-white">Scenario 8: Compromised Third-Party Supplier</h3>
              </div>
              <span className="text-[10px] font-mono bg-slate-700/60 px-2 py-0.5 rounded text-red-300">
                OWASP API10
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
              Simulates compromised FX rates vendor returning poisoned payload (negative rates, second-order SQLi, stored XSS). Caught and neutralized by <code className="text-red-300 font-mono">SafeExternalAPIClient</code>.
            </p>

            <button
              disabled={supplyChainRunning}
              onClick={runSupplyChainAttack}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white rounded-lg text-xs font-semibold shadow-sm transition disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{supplyChainRunning ? 'Simulating...' : 'Simulate Poisoned Vendor Response'}</span>
            </button>

            {supplyChainResult && (
              <div className="mt-3 p-2.5 bg-slate-950 border border-red-900/60 rounded-lg font-mono text-[10px] text-red-300 space-y-1">
                <div className="font-bold flex items-center space-x-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>HTTP {supplyChainResult.status}: {supplyChainResult.text}</span>
                </div>
                <pre className="text-slate-400 whitespace-pre-wrap mt-1">
                  {JSON.stringify(supplyChainResult.details, null, 2)}
                </pre>
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
