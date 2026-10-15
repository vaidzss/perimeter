import React, { useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { LandingPage } from './pages/LandingPage';
import { OverviewPage } from './pages/OverviewPage';
import { AlertsPage } from './pages/AlertsPage';
import { InvestigationPage } from './pages/InvestigationPage';
import { InventoryPage } from './pages/InventoryPage';
import { ApiDetailPage } from './pages/ApiDetailPage';
import { TrafficPage } from './pages/TrafficPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { DemoControlsPage } from './pages/DemoControlsPage';
import { IdentityAccessPage } from './pages/IdentityAccessPage';

function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
    const main = document.querySelector('main');
    if (main) main.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

export function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        {/* Modern High-Converting Architectural Landing Page */}
        <Route path="/" element={<LandingPage />} />

        {/* Internal SOC Management Console Routes */}
        <Route element={<Layout />}>
          <Route path="/overview" element={<OverviewPage />} />
          <Route path="/dashboard" element={<Navigate to="/overview" replace />} />
          <Route path="/console" element={<Navigate to="/overview" replace />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/alerts/:id" element={<InvestigationPage />} />
          <Route path="/identity" element={<IdentityAccessPage />} />
          <Route path="/inventory" element={<InventoryPage />} />
          <Route path="/inventory/:id" element={<ApiDetailPage />} />
          <Route path="/traffic" element={<TrafficPage />} />
          <Route path="/evaluation" element={<EvaluationPage />} />
          <Route path="/demo" element={<DemoControlsPage />} />
        </Route>

        {/* Fallback to landing */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

export default App;
