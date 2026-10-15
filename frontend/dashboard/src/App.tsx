import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { OverviewPage } from './pages/OverviewPage';
import { AlertsPage } from './pages/AlertsPage';
import { InvestigationPage } from './pages/InvestigationPage';
import { InventoryPage } from './pages/InventoryPage';
import { ApiDetailPage } from './pages/ApiDetailPage';
import { TrafficPage } from './pages/TrafficPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { DemoControlsPage } from './pages/DemoControlsPage';
import { IdentityAccessPage } from './pages/IdentityAccessPage';

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<OverviewPage />} />
        <Route path="alerts" element={<AlertsPage />} />
        <Route path="alerts/:id" element={<InvestigationPage />} />
        <Route path="identity" element={<IdentityAccessPage />} />
        <Route path="inventory" element={<InventoryPage />} />
        <Route path="inventory/:id" element={<ApiDetailPage />} />
        <Route path="traffic" element={<TrafficPage />} />
        <Route path="evaluation" element={<EvaluationPage />} />
        <Route path="demo" element={<DemoControlsPage />} />
      </Route>
    </Routes>
  );
}

export default App;
