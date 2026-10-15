import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { SendMoneyPage } from './pages/SendMoneyPage';
import { MerchantsPage } from './pages/MerchantsPage';
import { RedTeamDrawer } from './components/RedTeamDrawer';
import { AlertCircle, RefreshCw } from 'lucide-react';

const AppContent: React.FC = () => {
  const { user, isLoading } = useAuth();
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'send' | 'merchants'>('dashboard');
  const [prefilledPayVpa, setPrefilledPayVpa] = useState<string>('');
  const [drawerOpen, setDrawerOpen] = useState<boolean>(false);

  // Global Keyboard listener for Shift + R
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.shiftKey && (e.key === 'R' || e.key === 'r')) {
        e.preventDefault();
        setDrawerOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center space-y-3">
        <RefreshCw className="w-8 h-8 text-sky-600 animate-spin" />
        <span className="text-sm font-medium text-slate-600">Connecting to BharatPay secure gateway...</span>
      </div>
    );
  }

  const handleSelectMerchantForPay = (vpa: string) => {
    setPrefilledPayVpa(vpa);
    setCurrentTab('send');
  };

  return (
    <div className="min-h-screen flex flex-col justify-between bg-slate-50 text-slate-800 font-sans selection:bg-sky-100 selection:text-sky-900">
      <Navbar currentTab={currentTab} setCurrentTab={setCurrentTab} />

      <main className="flex-1 max-w-6xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {!user ? (
          <LoginPage />
        ) : (
          <>
            {currentTab === 'dashboard' && (
              <DashboardPage
                onNavigateToSend={() => setCurrentTab('send')}
                onNavigateToMerchants={() => setCurrentTab('merchants')}
              />
            )}
            {currentTab === 'send' && (
              <SendMoneyPage onBackToDashboard={() => setCurrentTab('dashboard')} />
            )}
            {currentTab === 'merchants' && (
              <MerchantsPage onSelectMerchantForPay={handleSelectMerchantForPay} />
            )}
          </>
        )}
      </main>

      {/* Red Team Attack Drawer */}
      <RedTeamDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

      {/* Persistent Watermark Footer */}
      <footer className="border-t border-slate-200 bg-white py-3 px-6 text-xs text-slate-500">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center space-x-2">
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-200">
              <AlertCircle className="w-3.5 h-3.5 mr-1 text-amber-600" />
              SYNTHETIC TEST DATA — CC6-IC07
            </span>
            <span className="text-slate-300">|</span>
            <span className="text-slate-500 text-[11px]">Fictional UPI Neobank Target System</span>
          </div>

          <div
            onClick={() => setDrawerOpen(true)}
            title="Open Red-Team Simulation Drawer"
            className="font-mono text-slate-400 hover:text-slate-700 text-[11px] flex items-center space-x-1.5 cursor-pointer transition"
          >
            <span>Red Team Simulation:</span>
            <kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-300 rounded text-slate-600 font-bold">Shift</kbd>
            <span>+</span>
            <kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-300 rounded text-slate-600 font-bold">R</kbd>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
