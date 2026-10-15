import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Lock, Smartphone, ShieldCheck, ArrowRight, AlertCircle } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const [identifier, setIdentifier] = useState('priya.sharma@bharatpay.com');
  const [password, setPassword] = useState('Password@123');
  const [useOtp, setUseOtp] = useState(false);
  const [otp, setOtp] = useState('123456');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (useOtp) {
        await login(identifier, undefined, otp);
      } else {
        await login(identifier, password, undefined);
      }
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickFill = (email: string, pass: string) => {
    setIdentifier(email);
    setPassword(pass);
    setUseOtp(false);
    setError(null);
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white border border-slate-200 rounded-2xl p-8 shadow-sm">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-12 h-12 bg-sky-50 text-sky-700 rounded-2xl flex items-center justify-center mx-auto mb-3 border border-sky-100">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">Welcome to BharatPay</h2>
          <p className="text-xs text-slate-500 mt-1">Enter your credentials or test OTP to access your account</p>
        </div>

        {error && (
          <div className="mb-5 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Email or 10-Digit Mobile Number
            </label>
            <div className="relative">
              <input
                type="text"
                required
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="priya.sharma@bharatpay.com"
                className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 text-slate-800 transition"
              />
            </div>
          </div>

          {!useOtp ? (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold text-slate-700">Password</label>
                <button
                  type="button"
                  onClick={() => setUseOtp(true)}
                  className="text-xs text-sky-600 hover:text-sky-700 font-medium"
                >
                  Use OTP-stub instead
                </button>
              </div>
              <div className="relative">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 text-slate-800 transition"
                />
              </div>
            </div>
          ) : (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold text-slate-700">Test OTP (Default: 123456)</label>
                <button
                  type="button"
                  onClick={() => setUseOtp(false)}
                  className="text-xs text-sky-600 hover:text-sky-700 font-medium"
                >
                  Use Password instead
                </button>
              </div>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  placeholder="123456"
                  maxLength={6}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-mono tracking-widest focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 text-slate-800 transition"
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-2.5 px-4 bg-sky-600 hover:bg-sky-700 text-white rounded-xl text-sm font-semibold shadow-sm transition flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In to Dashboard'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Quick Fill Test Accounts */}
        <div className="mt-6 pt-5 border-t border-slate-100">
          <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2.5 text-center">
            Quick-Fill Seeded Test Accounts
          </p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleQuickFill('priya.sharma@bharatpay.com', 'Password@123')}
              className="p-2 border border-slate-200 rounded-lg bg-slate-50 hover:bg-sky-50 hover:border-sky-200 text-left transition"
            >
              <div className="font-semibold text-slate-800">Priya Sharma</div>
              <div className="text-[11px] text-slate-500">₹48,500 • Verified</div>
            </button>
            <button
              type="button"
              onClick={() => handleQuickFill('rohit.verma@bharatpay.com', 'Password@123')}
              className="p-2 border border-slate-200 rounded-lg bg-slate-50 hover:bg-sky-50 hover:border-sky-200 text-left transition"
            >
              <div className="font-semibold text-slate-800">Rohit Verma</div>
              <div className="text-[11px] text-slate-500">₹1,25,000 • Verified</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
