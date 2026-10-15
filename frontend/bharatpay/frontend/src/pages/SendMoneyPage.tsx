import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { TransferReceipt } from '../types';
import { Send, CheckCircle2, AlertCircle, ArrowLeft, RefreshCw, ArrowRight } from 'lucide-react';

interface SendMoneyPageProps {
  onBackToDashboard: () => void;
}

export const SendMoneyPage: React.FC<SendMoneyPageProps> = ({ onBackToDashboard }) => {
  const { user } = useAuth();
  const [toVpa, setToVpa] = useState('');
  const [amountRupees, setAmountRupees] = useState('');
  const [note, setNote] = useState('Payment via BharatPay');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [receipt, setReceipt] = useState<TransferReceipt | null>(null);

  const quickAmounts = [100, 250, 500, 1000, 5000];

  const handleQuickAdd = (amt: number) => {
    const current = parseFloat(amountRupees) || 0;
    setAmountRupees((current + amt).toString());
  };

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    setError(null);

    const amt = parseFloat(amountRupees);
    if (isNaN(amt) || amt <= 0) {
      setError('Please enter a valid amount greater than ₹0');
      return;
    }

    const amountPaise = Math.round(amt * 100);
    const idempotencyKey = `idem_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

    setLoading(true);
    try {
      const res = await api.sendUPI(user.vpa, toVpa.trim(), amountPaise, note, idempotencyKey);
      setReceipt(res);
    } catch (err: any) {
      setError(err.message || 'Transfer failed. Check balance and limit.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (paise: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
    }).format(paise / 100);
  };

  return (
    <div className="max-w-xl mx-auto py-4">
      <div className="mb-4">
        <button
          onClick={onBackToDashboard}
          className="flex items-center space-x-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 transition"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Dashboard</span>
        </button>
      </div>

      {!receipt ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-700 flex items-center justify-center border border-sky-100">
              <Send className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">Send Money via UPI</h2>
              <p className="text-xs text-slate-500">Instant bank transfer with zero settlement delay</p>
            </div>
          </div>

          {error && (
            <div className="mb-5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleTransfer} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                From Account (VPA)
              </label>
              <input
                type="text"
                disabled
                value={user?.vpa || ''}
                className="w-full px-3.5 py-2.5 bg-slate-100 border border-slate-200 rounded-xl text-xs font-mono text-slate-600 cursor-not-allowed"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Recipient UPI ID / VPA
              </label>
              <input
                type="text"
                required
                value={toVpa}
                onChange={(e) => setToVpa(e.target.value)}
                placeholder="rohit.verma@bharatpay or swiggy@bharatpay"
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 text-slate-800 transition"
              />
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold text-slate-700">Amount (₹)</label>
                <span className="text-[11px] text-slate-400">Handled as integer paise</span>
              </div>
              <div className="relative">
                <span className="absolute left-3.5 top-2.5 text-base font-bold text-slate-400">₹</span>
                <input
                  type="number"
                  step="0.01"
                  min="1"
                  required
                  value={amountRupees}
                  onChange={(e) => setAmountRupees(e.target.value)}
                  placeholder="0.00"
                  className="w-full pl-8 pr-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-base font-bold focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 text-slate-900 transition"
                />
              </div>

              {/* Quick Amount Pills */}
              <div className="flex flex-wrap gap-1.5 mt-2">
                {quickAmounts.map((amt) => (
                  <button
                    key={amt}
                    type="button"
                    onClick={() => handleQuickAdd(amt)}
                    className="px-2.5 py-1 bg-slate-100 hover:bg-sky-50 hover:text-sky-700 border border-slate-200 rounded-lg text-xs font-medium text-slate-600 transition"
                  >
                    +₹{amt}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Remarks / Payment Note
              </label>
              <input
                type="text"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Dinner, groceries, split, etc."
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 text-slate-800 transition"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 px-4 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-semibold shadow-sm transition flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Processing UPI Transfer...</span>
                </>
              ) : (
                <>
                  <span>Pay Now</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>
      ) : (
        /* Transfer Receipt View */
        <div className="bg-white border border-slate-200 rounded-2xl p-6 sm:p-8 shadow-sm text-center">
          <div className="w-14 h-14 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4 border border-emerald-100">
            <CheckCircle2 className="w-8 h-8" />
          </div>

          <h2 className="text-xl font-bold text-slate-900">Transfer Successful</h2>
          <p className="text-xs text-slate-500 mt-0.5">UPI Payment completed with zero errors</p>

          <div className="text-3xl font-extrabold text-slate-900 my-4">
            {formatCurrency(receipt.amount_paise)}
          </div>

          <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 text-xs space-y-2.5 text-left mb-6">
            <div className="flex justify-between">
              <span className="text-slate-400">Txn Reference:</span>
              <span className="font-mono font-semibold text-slate-800">{receipt.txn_reference}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Recipient VPA:</span>
              <span className="font-mono font-semibold text-slate-800">{receipt.to_vpa}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Payment Note:</span>
              <span className="text-slate-700">{receipt.note}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Updated Balance:</span>
              <span className="font-semibold text-emerald-700">{formatCurrency(receipt.remaining_balance_paise)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Daily Limit Left:</span>
              <span className="font-semibold text-slate-700">{formatCurrency(receipt.daily_limit_remaining_paise)}</span>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => {
                setReceipt(null);
                setAmountRupees('');
                setToVpa('');
              }}
              className="flex-1 py-2.5 px-4 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition"
            >
              Send Another Payment
            </button>
            <button
              onClick={onBackToDashboard}
              className="flex-1 py-2.5 px-4 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-xs font-semibold transition"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
