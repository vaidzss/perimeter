import React from 'react';
import { useAuth } from '../context/AuthContext';
import { LogOut, User as UserIcon, Send, Store, LayoutDashboard } from 'lucide-react';

interface NavbarProps {
  currentTab: 'dashboard' | 'send' | 'merchants';
  setCurrentTab: (tab: 'dashboard' | 'send' | 'merchants') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setCurrentTab }) => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-3.5 sticky top-0 z-20 shadow-[0_1px_2px_rgba(0,0,0,0.03)]">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Brand identity */}
        <div className="flex items-center space-x-6">
          <div 
            onClick={() => setCurrentTab('dashboard')} 
            className="flex items-center space-x-3 cursor-pointer group"
          >
            <div className="w-9 h-9 rounded-xl bg-sky-600 flex items-center justify-center text-white font-bold text-base shadow-sm group-hover:bg-sky-700 transition">
              BP
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-lg font-bold tracking-tight text-slate-900">BharatPay</span>
                <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-sky-50 text-sky-700 rounded border border-sky-200">
                  NEOBANK
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Next-Gen UPI Banking</p>
            </div>
          </div>

          {/* Nav Tabs */}
          {user && (
            <nav className="hidden md:flex items-center space-x-1 pl-4 border-l border-slate-200">
              <button
                onClick={() => setCurrentTab('dashboard')}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  currentTab === 'dashboard'
                    ? 'bg-slate-100 text-sky-700 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <LayoutDashboard className="w-3.5 h-3.5" />
                <span>Dashboard</span>
              </button>

              <button
                onClick={() => setCurrentTab('send')}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  currentTab === 'send'
                    ? 'bg-slate-100 text-sky-700 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Send className="w-3.5 h-3.5" />
                <span>Send Money</span>
              </button>

              <button
                onClick={() => setCurrentTab('merchants')}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  currentTab === 'merchants'
                    ? 'bg-slate-100 text-sky-700 font-semibold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Store className="w-3.5 h-3.5" />
                <span>Merchants</span>
              </button>
            </nav>
          )}
        </div>

        {/* User profile & actions */}
        <div className="flex items-center space-x-3">
          {user ? (
            <div className="flex items-center space-x-3">
              <div className="text-right hidden sm:block">
                <div className="text-xs font-semibold text-slate-800">{user.full_name}</div>
                <div className="text-[11px] font-mono text-slate-500">{user.vpa}</div>
              </div>
              <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600">
                <UserIcon className="w-4 h-4" />
              </div>
              <button
                onClick={logout}
                title="Sign out"
                className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <div className="text-xs text-slate-500">Sign In to continue</div>
          )}
        </div>
      </div>
    </header>
  );
};
