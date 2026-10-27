import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { TradingViewChart } from '../charts/TradingViewChart';
import { CandlestickChart } from '../charts/CandlestickChart';
import { KpiCard } from '../components/KpiCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { DollarSign, BarChart3, Activity, Layers, SlidersHorizontal, BarChart2 } from 'lucide-react';

export const StockExplorer: React.FC<{ symbol: string }> = ({ symbol }) => {
  const [chartMode, setChartMode] = useState<'tradingview' | 'analytical'>('analytical');

  const { data: prices, isLoading: pricesLoading } = useQuery({
    queryKey: ['prices', symbol],
    queryFn: () => api.getPriceHistory(symbol),
  });

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['stats', symbol],
    queryFn: () => api.getStatistics(symbol),
  });

  if (pricesLoading || statsLoading) {
    return <LoadingSpinner message={`Loading financial series for ${symbol}...`} />;
  }

  const latestPrice = prices && prices.length > 0 ? prices[prices.length - 1] : null;
  const desc = stats?.descriptive || stats?.return_summary;
  const isIndianStock = symbol.includes('.NS') || (!symbol.includes('.') && symbol.length > 4 && !['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'SPY', 'QQQ'].includes(symbol));
  const currPrefix = isIndianStock ? '₹' : '$';

  return (
    <div className="space-y-6">
      {/* Header Info & Chart Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <span>{symbol} Financial Series Explorer</span>
            <span className="text-xs font-mono font-normal text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/10">
              Whole-Exchange Coverage
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time interactive charting, historical technical metrics, and dispersion analysis.
          </p>
        </div>

        <div className="flex items-center space-x-1.5 bg-[#111827] p-1 rounded-xl border border-white/10">
          <button
            onClick={() => setChartMode('tradingview')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              chartMode === 'tradingview'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
            }`}
          >
            <BarChart2 className="w-3.5 h-3.5" />
            <span>TradingView Widget</span>
          </button>
          <button
            onClick={() => setChartMode('analytical')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              chartMode === 'analytical'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
            }`}
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Analytical Candles</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Latest Close"
          value={latestPrice ? `${currPrefix}${latestPrice.close.toFixed(2)}` : `${currPrefix}0.00`}
          subtext={`High: ${currPrefix}${latestPrice?.high.toFixed(2)} | Low: ${currPrefix}${latestPrice?.low.toFixed(2)}`}
          icon={<DollarSign className="w-5 h-5" />}
        />
        <KpiCard
          label="20-Day Mean Return"
          value={desc ? `${(desc.mean * 100).toFixed(3)}%` : '0.00%'}
          subtext={`Median: ${(desc?.median ? desc.median * 100 : 0).toFixed(3)}%`}
          icon={<BarChart3 className="w-5 h-5" />}
          trend={desc && desc.mean >= 0 ? 'positive' : 'negative'}
        />
        <KpiCard
          label="Annualized Volatility"
          value={desc ? `${(desc.std_dev * Math.sqrt(252) * 100).toFixed(1)}%` : '0.0%'}
          subtext={`Daily Std Dev: ${(desc?.std_dev ? desc.std_dev * 100 : 0).toFixed(2)}%`}
          icon={<Activity className="w-5 h-5" />}
          trend="neutral"
        />
        <KpiCard
          label="Volume Liquidity"
          value={latestPrice ? `${(latestPrice.volume / 1e6).toFixed(2)}M` : '0M'}
          subtext="Latest daily shares traded"
          icon={<Layers className="w-5 h-5" />}
        />
      </div>

      {/* Primary Chart View: Official TradingView Embed Widget */}
      {chartMode === 'tradingview' ? (
        <TradingViewChart symbol={symbol} />
      ) : (
        prices && prices.length > 0 && (
          <CandlestickChart prices={prices} symbol={symbol} />
        )
      )}

      {/* Detailed Technical Attributes Summary */}
      {desc && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
          <div className="card-surface p-4">
            <h4 className="text-slate-400 text-[11px] uppercase tracking-wider font-semibold mb-2">
              Central Tendency
            </h4>
            <div className="space-y-1.5 text-slate-300">
              <div className="flex justify-between">
                <span>Mean Return:</span>
                <span className="text-white font-bold">{(desc.mean * 100).toFixed(4)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Median Return:</span>
                <span className="text-white">{(desc.median * 100).toFixed(4)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Trimmed Mean (5%):</span>
                <span className="text-white">{(desc.trimmed_mean * 100).toFixed(4)}%</span>
              </div>
            </div>
          </div>

          <div className="card-surface p-4">
            <h4 className="text-slate-400 text-[11px] uppercase tracking-wider font-semibold mb-2">
              Dispersion & Range
            </h4>
            <div className="space-y-1.5 text-slate-300">
              <div className="flex justify-between">
                <span>Standard Deviation:</span>
                <span className="text-white font-bold">{(desc.std_dev * 100).toFixed(4)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Variance:</span>
                <span className="text-white">{desc.variance.toExponential(4)}</span>
              </div>
              <div className="flex justify-between">
                <span>Interquartile Range (IQR):</span>
                <span className="text-white">{(desc.iqr * 100).toFixed(4)}%</span>
              </div>
            </div>
          </div>

          <div className="card-surface p-4">
            <h4 className="text-slate-400 text-[11px] uppercase tracking-wider font-semibold mb-2">
              Shape & Extremes
            </h4>
            <div className="space-y-1.5 text-slate-300">
              <div className="flex justify-between">
                <span>Skewness:</span>
                <span className={`font-bold ${desc.skewness < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {desc.skewness.toFixed(4)}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Excess Kurtosis:</span>
                <span className="text-white font-bold">{desc.kurtosis.toFixed(4)}</span>
              </div>
              <div className="flex justify-between">
                <span>Outlier Observations:</span>
                <span className="text-amber-400 font-bold">
                  {desc.outliers_count} ({desc.outliers_pct.toFixed(2)}%)
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
