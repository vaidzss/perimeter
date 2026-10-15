import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { StatementData } from '../types';
import { 
  ArrowUpRight, 
  ArrowDownLeft, 
  Copy, 
  Check, 
  ShieldCheck, 
  Clock, 
  Wallet, 
  Send, 
  Store,
  RefreshCw
} from 'lucide-react';

interface DashboardPageProps {
  onNavigateToSend: () => void;
  onNavigateToMerchants: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigateToSend, onNavigateToMerchants }) => {
  const { user } = useAuth();
  const [statement, setStatement] = useState<StatementData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedVpa, setCopiedVpa] = useState<boolean>(false);

  const fetchStatement = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStatement(user.account_id);
      setStatement(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load statement');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatement();
  }, [user]);

  const copyVpa = () => {
    if (statement?.vpa) {
      navigator.clipboard.writeText(statement.vpa);
      setCopiedVpa(true);
      setTimeout(() => setCopiedVpa(false), 2000);
    }
  };

  const formatCurrency = (paise: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
    }).format(paise / 100);
  };

  if (loading && !statement) {
    return (
      <div className="py-20 flex flex-col items-center justify-center space-y-3">
        <RefreshCw className="w-6 h-6 text-sky-600 animate-spin" />
        <span className="text-xs text-slate-500 font-medium">Loading account details...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto my-8 p-6 bg-white border border-rose-200 rounded-2xl shadow-sm">
        <div className="text-rose-600 font-semibold mb-2">Error Loading Account</div>
        <p className="text-xs text-slate-600 mb-4">{error}</p>
        <button
          onClick={fetchStatement}
          className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-800 transition"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Top Welcome & Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Account Overview</h1>
          <p className="text-xs text-slate-500 mt-0.5">Welcome back, {user?.full_name}</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={fetchStatement}
            title="Refresh Balance"
            className="p-2 border border-slate-200 bg-white hover:bg-slate-50 rounded-xl text-slate-600 transition"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={onNavigateToSend}
            className="flex items-center space-x-1.5 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-semibold shadow-sm transition"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Send Money</span>
          </button>
          <button
            onClick={onNavigateToMerchants}
            className="flex items-center space-x-1.5 px-4 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold shadow-sm transition"
          >
            <Store className="w-3.5 h-3.5" />
            <span>Merchants</span>
          </button>
        </div>
      </div>

      {/* Primary Account Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Main Balance Card */}
        <div className="md:col-span-2 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Total Available Balance
              </span>
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5"></span>
                Active Savings
              </span>
            </div>
            <div className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900 mb-2">
              {formatCurrency(statement?.balance_paise || 0)}
            </div>
            <p className="text-xs text-slate-400">
              Primary Account: <span className="font-mono text-slate-600">{statement?.account_number_masked}</span> • IFSC: <span className="font-mono text-slate-600">{statement?.ifsc_code}</span>
            </p>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-500">UPI VPA:</span>
              <span className="px-2.5 py-1 bg-slate-100 rounded-lg font-mono text-xs font-semibold text-slate-800">
                {statement?.vpa}
              </span>
              <button
                onClick={copyVpa}
                className="p-1 text-slate-400 hover:text-slate-600 transition"
                title="Copy VPA"
              >
                {copiedVpa ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>

            <div className="text-xs text-slate-500">
              Daily Limit: <span className="font-semibold text-slate-700">{formatCurrency(statement?.daily_limit_paise || 0)}</span>
            </div>
          </div>
        </div>

        {/* KYC & Identity Status Card */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <ShieldCheck className="w-5 h-5 text-sky-600" />
              <h2 className="text-sm font-bold text-slate-900">Identity & KYC</h2>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Verified tier for digital UPI & IMPS limits
            </p>

            <div className="space-y-3">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <div className="text-[11px] text-slate-400 uppercase font-semibold">Verification Status</div>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs font-bold text-slate-800">Full KYC</span>
                  <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-100 text-emerald-800 rounded-full">
                    {statement?.kyc_status}
                  </span>
                </div>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <div className="text-[11px] text-slate-400 uppercase font-semibold">Masked Tax ID (PAN)</div>
                <div className="font-mono text-xs font-semibold text-slate-800 mt-1">
                  {statement?.masked_pan}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400 text-center">
            Synthetic Customer Profile
          </div>
        </div>
      </div>

      {/* Recent Transactions Section */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Recent Transactions</h2>
            <p className="text-xs text-slate-500">Last 10 UPI transfers & settlements</p>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {statement?.transactions.length || 0} Records
          </span>
        </div>

        {(!statement?.transactions || statement.transactions.length === 0) ? (
          <div className="text-center py-10 text-xs text-slate-400">
            No transaction records found for this account.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {statement.transactions.map((txn) => {
              const isCredit = txn.to_vpa === statement.vpa;
              return (
                <div key={txn.id} className="py-3.5 flex items-center justify-between hover:bg-slate-50/50 transition px-2 rounded-xl">
                  <div className="flex items-center space-x-3">
                    <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                      isCredit ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {isCredit ? <ArrowDownLeft className="w-4 h-4" /> : <ArrowUpRight className="w-4 h-4" />}
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-slate-800">
                        {txn.note || (isCredit ? 'Received UPI Payment' : 'Paid to Merchant')}
                      </div>
                      <div className="text-[11px] font-mono text-slate-400">
                        {isCredit ? `From: ${txn.from_vpa}` : `To: ${txn.to_vpa}`} • {txn.txn_reference}
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className={`text-xs font-bold ${
                      isCredit ? 'text-emerald-600' : 'text-slate-900'
                    }`}>
                      {isCredit ? '+' : '-'}{formatCurrency(txn.amount_paise)}
                    </div>
                    <div className="text-[10px] text-slate-400">
                      {new Date(txn.created_at).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
