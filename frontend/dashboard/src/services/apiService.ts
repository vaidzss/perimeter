import {
  OverviewPosture,
  ApiInventoryItem,
  ApiDetail,
  SecurityAlert,
  TrafficAnalytics,
  InvestigationData
} from '../types/apiSecurity';
import {
  mockOverviewPosture,
  mockInventory,
  mockApiDetails,
  mockAlerts,
  mockTrafficAnalytics,
  mockInvestigationData
} from '../data/mockData';

// Storage key for mode preference
const MODE_STORAGE_KEY = 'cybercup_api_mode';

class ApiService {
  private baseUrl: string = '/api/v1';
  private useMock: boolean = false;
  private isBackendOnline: boolean = false;

  constructor() {
    const savedMode = localStorage.getItem(MODE_STORAGE_KEY);
    this.useMock = savedMode === 'mock';
  }

  public setUseMock(val: boolean) {
    this.useMock = val;
    localStorage.setItem(MODE_STORAGE_KEY, val ? 'mock' : 'real');
  }

  public getUseMock(): boolean {
    return this.useMock;
  }

  public getBackendStatus(): boolean {
    return this.isBackendOnline;
  }

  public async checkHealth(): Promise<boolean> {
    try {
      const res = await fetch(`${this.baseUrl}/health`, { method: 'GET', signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        this.isBackendOnline = true;
        return true;
      }
    } catch (e) {
      this.isBackendOnline = false;
    }
    return false;
  }

  public async getOverviewPosture(): Promise<OverviewPosture> {
    if (this.useMock) return mockOverviewPosture;
    try {
      const res = await fetch(`${this.baseUrl}/overview/posture`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      this.isBackendOnline = true;
      return await res.json();
    } catch (err) {
      console.warn('[ApiService] Falling back to mock overview posture:', err);
      this.isBackendOnline = false;
      return mockOverviewPosture;
    }
  }

  public async getInventory(params?: { search?: string; status?: string; minRisk?: number; method?: string }): Promise<ApiInventoryItem[]> {
    if (this.useMock) {
      let filtered = [...mockInventory];
      if (params?.search) {
        const s = params.search.toLowerCase();
        filtered = filtered.filter(item =>
          item.path.toLowerCase().includes(s) ||
          item.service.toLowerCase().includes(s) ||
          item.tags.some(t => t.toLowerCase().includes(s))
        );
      }
      if (params?.status && params.status !== 'all') {
        filtered = filtered.filter(item => item.status === params.status);
      }
      if (params?.method && params.method !== 'all') {
        filtered = filtered.filter(item => item.method === params.method);
      }
      if (params?.minRisk) {
        filtered = filtered.filter(item => item.riskScore >= params.minRisk!);
      }
      return filtered;
    }

    try {
      const url = new URL(`${window.location.origin}${this.baseUrl}/inventory`);
      if (params?.search) url.searchParams.set('search', params.search);
      if (params?.status && params.status !== 'all') url.searchParams.set('status', params.status);
      if (params?.method && params.method !== 'all') url.searchParams.set('method', params.method);
      if (params?.minRisk) url.searchParams.set('minRisk', String(params.minRisk));

      const res = await fetch(url.toString());
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      this.isBackendOnline = true;
      return await res.json();
    } catch (err) {
      console.warn('[ApiService] Falling back to mock inventory:', err);
      this.isBackendOnline = false;
      return mockInventory;
    }
  }

  public async getApiDetail(id: string): Promise<ApiDetail> {
    if (this.useMock) {
      if (mockApiDetails[id]) return mockApiDetails[id];
      const inv = mockInventory.find(i => i.id === id);
      if (inv) {
        return {
          ...inv,
          riskBreakdown: { factors: [], remediationGuidance: ['Review endpoint posture'] },
          parameters: [],
          samplePayloads: { request: {}, response: {} },
          schemaDrift: { hasDrift: false, undocumentedFields: [], missingRequiredFields: [], lastSpecSync: 'N/A' },
          mitigationStatus: { quarantined: false, virtualPatched: false, wafRuleActive: false },
        };
      }
      throw new Error('API not found');
    }

    try {
      const res = await fetch(`${this.baseUrl}/inventory/${id}`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      this.isBackendOnline = true;
      return await res.json();
    } catch (err) {
      console.warn('[ApiService] Falling back to mock API detail:', err);
      this.isBackendOnline = false;
      return mockApiDetails[id] || (mockInventory.find(i => i.id === id) as any);
    }
  }

  public async getAlerts(params?: { severity?: string; status?: string; category?: string }): Promise<SecurityAlert[]> {
    if (this.useMock) {
      let filtered = [...mockAlerts];
      if (params?.severity && params.severity !== 'all') {
        filtered = filtered.filter(a => a.severity === params.severity);
      }
      if (params?.status && params.status !== 'all') {
        filtered = filtered.filter(a => a.status === params.status);
      }
      return filtered;
    }

    try {
      const url = new URL(`${window.location.origin}${this.baseUrl}/alerts`);
      if (params?.severity && params.severity !== 'all') url.searchParams.set('severity', params.severity);
      if (params?.status && params.status !== 'all') url.searchParams.set('status', params.status);
      if (params?.category && params.category !== 'all') url.searchParams.set('category', params.category);

      const res = await fetch(url.toString());
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      this.isBackendOnline = true;
      return await res.json();
    } catch (err) {
      console.warn('[ApiService] Falling back to mock alerts:', err);
      this.isBackendOnline = false;
      return mockAlerts;
    }
  }

  public async getTrafficAnalytics(): Promise<TrafficAnalytics> {
    if (this.useMock) return mockTrafficAnalytics;
    try {
      const res = await fetch(`${this.baseUrl}/analytics/traffic`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      this.isBackendOnline = true;
      return await res.json();
    } catch (err) {
      console.warn('[ApiService] Falling back to mock traffic analytics:', err);
      this.isBackendOnline = false;
      return mockTrafficAnalytics;
    }
  }

  public async getInvestigation(alertId: string): Promise<InvestigationData> {
    if (this.useMock) {
      if (mockInvestigationData.alert.id === alertId) {
        return mockInvestigationData;
      }
      const alert = mockAlerts.find(a => a.id === alertId) || mockAlerts[0];
      return {
        ...mockInvestigationData,
        alert,
      };
    }

    try {
      const res = await fetch(`${this.baseUrl}/investigation/${alertId}`);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      this.isBackendOnline = true;
      return await res.json();
    } catch (err) {
      console.warn('[ApiService] Falling back to mock investigation data:', err);
      this.isBackendOnline = false;
      return mockInvestigationData;
    }
  }

  public async blockActor(ip: string, reason?: string): Promise<{ success: boolean; message: string }> {
    if (this.useMock) {
      return { success: true, message: `[Mock Mode] Actor ${ip} marked as globally blocked.` };
    }
    try {
      const res = await fetch(`${this.baseUrl}/actions/block-actor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip, reason }),
      });
      return await res.json();
    } catch (err) {
      return { success: false, message: 'Failed to communicate with REST endpoint' };
    }
  }

  public async quarantineApi(apiId: string): Promise<{ success: boolean; message: string }> {
    if (this.useMock) {
      return { success: true, message: `[Mock Mode] API ${apiId} successfully quarantined.` };
    }
    try {
      const res = await fetch(`${this.baseUrl}/actions/quarantine-api`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ apiId }),
      });
      return await res.json();
    } catch (err) {
      return { success: false, message: 'Failed to communicate with REST endpoint' };
    }
  }

  public async mitigateAlert(alertId: string): Promise<{ success: boolean; message: string }> {
    if (this.useMock) {
      return { success: true, message: `[Mock Mode] Alert ${alertId} marked as mitigated.` };
    }
    try {
      const res = await fetch(`${this.baseUrl}/actions/mitigate-alert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alertId }),
      });
      return await res.json();
    } catch (err) {
      return { success: false, message: 'Failed to communicate with REST endpoint' };
    }
  }

  public async simulateLiveAttack(type: 'bola' | 'shadow' = 'bola'): Promise<{ success: boolean; message: string; alert?: SecurityAlert }> {
    if (this.useMock) {
      return { success: true, message: '[Mock Mode] Attack simulation triggered' };
    }
    try {
      const res = await fetch(`${this.baseUrl}/simulate-attack`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type }),
      });
      return await res.json();
    } catch (err) {
      return { success: false, message: 'Failed to trigger attack simulation on REST API' };
    }
  }
}

export const apiService = new ApiService();
