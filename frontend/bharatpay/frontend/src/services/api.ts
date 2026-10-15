import { UserProfile, StatementData, PaginatedMerchants, TransferReceipt } from '../types';

const API_BASE = '/api/v2';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('bharatpay_token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

export const api = {
  async login(identifier: string, password?: string, otp?: string): Promise<{ access_token: string; jti: string; user_id: string; account_id: number }> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ identifier, password, otp }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Authentication failed' }));
      throw new Error(err.detail || 'Login failed');
    }
    return res.json();
  },

  async getMe(): Promise<UserProfile> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      throw new Error('Failed to fetch user profile');
    }
    return res.json();
  },

  async getStatement(accountId: number): Promise<StatementData> {
    const res = await fetch(`${API_BASE}/accounts/${accountId}/statement`, {
      headers: getAuthHeaders(),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to fetch statement' }));
      throw new Error(err.detail || `Error fetching statement (${res.status})`);
    }
    return res.json();
  },

  async getMerchants(page: number = 1, limit: number = 20, search?: string): Promise<PaginatedMerchants> {
    const params = new URLSearchParams({ page: page.toString(), limit: limit.toString() });
    if (search && search.trim()) {
      params.append('search', search.trim());
    }
    const res = await fetch(`${API_BASE}/upi/merchants?${params.toString()}`);
    if (!res.ok) {
      throw new Error('Failed to fetch merchants');
    }
    return res.json();
  },

  async sendUPI(fromVpa: string, toVpa: string, amountPaise: number, note?: string, idempotencyKey?: string): Promise<TransferReceipt> {
    const res = await fetch(`${API_BASE}/payments/upi-transfer`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        from_vpa: fromVpa,
        to_vpa: toVpa,
        amount_paise: amountPaise,
        note: note || 'UPI Payment',
        idempotency_key: idempotencyKey,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Payment failed' }));
      throw new Error(err.detail || 'Transfer failed');
    }
    return res.json();
  },
};
