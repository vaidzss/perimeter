import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { MerchantItem } from '../types';
import { Store, Search, ShieldCheck, Star, ChevronLeft, ChevronRight, ArrowRight, RefreshCw } from 'lucide-react';

interface MerchantsPageProps {
  onSelectMerchantForPay: (vpa: string) => void;
}

export const MerchantsPage: React.FC<MerchantsPageProps> = ({ onSelectMerchantForPay }) => {
  const [merchants, setMerchants] = useState<MerchantItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchMerchants = async (currentPage: number, searchTerm?: string) => {
    setLoading(true);
    try {
      const data = await api.getMerchants(currentPage, 12, searchTerm);
      setMerchants(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err) {
      console.error('Error fetching merchants:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMerchants(page, search);
  }, [page]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchMerchants(1, search);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header and Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Verified Merchant Directory</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Discover {total}+ verified Indian retail, food, transit, and utility partners
          </p>
        </div>

        <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-72">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search brand, category, or VPA..."
            className="w-full pl-9 pr-3.5 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 text-slate-800 transition shadow-sm"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
        </form>
      </div>

      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center space-y-3">
          <RefreshCw className="w-6 h-6 text-sky-600 animate-spin" />
          <span className="text-xs text-slate-500">Searching merchant registry...</span>
        </div>
      ) : (
        <>
          {merchants.length === 0 ? (
            <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center shadow-sm">
              <Store className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              <div className="text-sm font-semibold text-slate-700">No merchants matched your query</div>
              <p className="text-xs text-slate-400 mt-1">Try searching for Swiggy, Blinkit, Uber, or Electricity</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {merchants.map((merchant) => (
                <div
                  key={merchant.id}
                  className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between mb-2.5">
                      <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 rounded-lg bg-sky-50 text-sky-700 flex items-center justify-center font-bold text-xs border border-sky-100">
                          {merchant.business_name.charAt(0)}
                        </div>
                        <div>
                          <div className="flex items-center space-x-1.5">
                            <span className="text-xs font-bold text-slate-900 leading-tight">
                              {merchant.business_name}
                            </span>
                            {merchant.verified && (
                              <span title="Verified UPI Merchant">
                                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                              </span>
                            )}
                          </div>
                          <span className="text-[10px] font-medium text-slate-400 uppercase tracking-wider block">
                            {merchant.category}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center space-x-1 px-1.5 py-0.5 bg-amber-50 rounded text-[11px] font-semibold text-amber-800 border border-amber-200">
                        <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                        <span>{merchant.rating}</span>
                      </div>
                    </div>

                    <div className="mt-3 p-2 bg-slate-50 rounded-lg border border-slate-100">
                      <div className="text-[10px] text-slate-400">VPA Address</div>
                      <div className="font-mono text-xs font-semibold text-slate-800 truncate">
                        {merchant.vpa}
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-[10px] text-slate-400 font-mono">{merchant.merchant_code}</span>
                    <button
                      onClick={() => onSelectMerchantForPay(merchant.vpa)}
                      className="flex items-center space-x-1 text-xs font-semibold text-sky-600 hover:text-sky-700 transition"
                    >
                      <span>Pay</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-4 border-t border-slate-200">
              <span className="text-xs text-slate-500">
                Page <span className="font-semibold text-slate-800">{page}</span> of{' '}
                <span className="font-semibold text-slate-800">{totalPages}</span> ({total} merchants)
              </span>

              <div className="flex items-center space-x-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  className="flex items-center space-x-1 px-3 py-1.5 border border-slate-200 bg-white rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>Previous</span>
                </button>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  className="flex items-center space-x-1 px-3 py-1.5 border border-slate-200 bg-white rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
                >
                  <span>Next</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
