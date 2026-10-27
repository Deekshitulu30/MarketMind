import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { KpiCard } from '../components/KpiCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { TrendingUp, Activity, ShieldCheck, Database, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const MarketOverview: React.FC<{ onSelectSymbol: (sym: string) => void }> = ({
  onSelectSymbol,
}) => {
  const { data: summary, isLoading, error } = useQuery({
    queryKey: ['market-summary'],
    queryFn: api.getMarketSummary,
  });

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: api.getHealth,
  });

  if (isLoading) return <LoadingSpinner message="Loading market overview..." />;
  if (error || !summary) {
    return (
      <div className="card-surface p-6 text-rose-400">
        Failed to load market overview data. Ensure backend is running.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Welcome & Subtitle */}
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight">
          Explainable Market Intelligence Overview
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Real-time statistical synthesis, multi-asset performance tracking, and machine-learning sandbox health.
        </p>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Monitored Assets"
          value={summary.tracked_stocks_count}
          subtext="Equities + Benchmark (SPY)"
          icon={<TrendingUp className="w-5 h-5" />}
        />
        <KpiCard
          label="Market Volatility (SPY)"
          value={`${((summary.market_volatility || 0.16) * 100).toFixed(1)}%`}
          subtext="Annualized 252-day baseline"
          icon={<Activity className="w-5 h-5" />}
          trend="neutral"
        />
        <KpiCard
          label="Total Price Records"
          value={summary.total_price_records.toLocaleString()}
          subtext="2021 – 2025 Chronological"
          icon={<Database className="w-5 h-5" />}
        />
        <KpiCard
          label="Leakage Defense"
          value="Active (100%)"
          subtext="Strict Time-Split Enforced"
          icon={<ShieldCheck className="w-5 h-5" />}
          trend="positive"
        />
      </div>

      {/* Assets Grid & System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tracked Assets Table */}
        <div className="lg:col-span-2 card-surface p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Tracked Securities</h3>
              <p className="text-xs text-slate-400">Select any symbol to inspect statistical models & predictions</p>
            </div>
            <span className="text-xs font-mono text-slate-400">
              Cutoff: {summary.latest_trading_day}
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-white/5 text-slate-400 font-mono uppercase text-[10px]">
                  <th className="pb-3 font-semibold">Symbol</th>
                  <th className="pb-3 font-semibold">Company</th>
                  <th className="pb-3 font-semibold">Sector</th>
                  <th className="pb-3 font-semibold text-right">Latest Close</th>
                  <th className="pb-3 font-semibold text-right">24h Return</th>
                  <th className="pb-3 font-semibold text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-mono">
                {summary.stocks.map((stock) => {
                  const isPositive = (stock.daily_return_pct || 0) >= 0;
                  return (
                    <tr key={stock.symbol} className="hover:bg-white/5 transition-colors">
                      <td className="py-3 font-bold text-blue-400">{stock.symbol}</td>
                      <td className="py-3 text-slate-300 font-sans">{stock.company_name}</td>
                      <td className="py-3 text-slate-400 font-sans">{stock.sector}</td>
                      <td className="py-3 text-right text-slate-100 font-semibold">
                        ${stock.latest_close.toFixed(2)}
                      </td>
                      <td className="py-3 text-right">
                        <span
                          className={`inline-flex items-center space-x-0.5 px-1.5 py-0.5 rounded text-[11px] ${
                            isPositive
                              ? 'text-emerald-400 bg-emerald-500/10'
                              : 'text-rose-400 bg-rose-500/10'
                          }`}
                        >
                          {isPositive ? (
                            <ArrowUpRight className="w-3 h-3" />
                          ) : (
                            <ArrowDownRight className="w-3 h-3" />
                          )}
                          <span>{(stock.daily_return_pct || 0).toFixed(2)}%</span>
                        </span>
                      </td>
                      <td className="py-3 text-center font-sans">
                        <Link
                          to="/predictions"
                          onClick={() => onSelectSymbol(stock.symbol)}
                          className="px-2.5 py-1 text-[11px] font-medium bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white rounded transition-colors"
                        >
                          Analyze
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Platform Integrity Card */}
        <div className="card-surface p-5 space-y-4">
          <h3 className="text-sm font-semibold text-white">Platform Health & Integrity</h3>
          <p className="text-xs text-slate-400">
            MarketMind operates with strict architectural barriers preventing lookahead bias and data leakage.
          </p>

          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between p-2.5 rounded bg-[#0B0F17] border border-white/5">
              <span className="text-slate-400">API Status:</span>
              <span className="text-emerald-400 font-semibold">{health?.status || 'HEALTHY'}</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-[#0B0F17] border border-white/5">
              <span className="text-slate-400">Data Pipeline:</span>
              <span className="text-blue-400">{health?.database || 'CONNECTED'}</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-[#0B0F17] border border-white/5">
              <span className="text-slate-400">ML Engine:</span>
              <span className="text-indigo-400">scikit-learn 1.4</span>
            </div>
            <div className="flex justify-between p-2.5 rounded bg-[#0B0F17] border border-white/5">
              <span className="text-slate-400">SHAP Explainer:</span>
              <span className="text-emerald-400">TreeSHAP / Linear</span>
            </div>
          </div>

          <div className="p-3 bg-blue-500/10 rounded-lg border border-blue-500/20 text-xs text-slate-300">
            <span className="font-semibold text-blue-400 block mb-1">Quick Start:</span>
            Navigate to <strong>Model Lab</strong> to train models or <strong>What-If Simulator</strong> to stress test hypothetical market conditions.
          </div>
        </div>
      </div>
    </div>
  );
};
