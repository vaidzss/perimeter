export interface UserProfile {
  user_code: string;
  email: string;
  phone: string;
  full_name: string;
  role: string;
  account_id: number;
  account_number_masked: string;
  vpa: string;
  kyc_status: string;
  masked_pan: string;
  watermark: string;
}

export interface TransactionItem {
  id: number;
  txn_reference: string;
  from_vpa: string;
  to_vpa: string;
  amount_paise: number;
  note: string;
  status: string;
  created_at: string;
}

export interface StatementData {
  account_id: number;
  account_number_masked: string;
  ifsc_code: string;
  balance_paise: number;
  currency: string;
  daily_limit_paise: number;
  vpa: string;
  kyc_status: string;
  masked_pan: string;
  transactions: TransactionItem[];
  watermark: string;
}

export interface MerchantItem {
  id: number;
  merchant_code: string;
  business_name: string;
  vpa: string;
  category: string;
  verified: boolean;
  rating: number;
}

export interface PaginatedMerchants {
  items: MerchantItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface TransferReceipt {
  txn_reference: string;
  status: string;
  from_vpa: string;
  to_vpa: string;
  amount_paise: number;
  remaining_balance_paise: number;
  daily_limit_remaining_paise: number;
  note: string;
  created_at: string;
  idempotent_replay: boolean;
}
