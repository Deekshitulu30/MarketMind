import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { KpiCard } from '../components/KpiCard';
import { ModelReferencePanel } from '../components/ModelReferencePanel';
import { useLivePrediction, StreamMode } from '../hooks/useLivePrediction';
import {
  TrendingUp,
  TrendingDown,
  Percent,
  Calendar,
  AlertCircle,
  Cpu,
  Shield,
  Layers,
  Activity,
  Radio,
  RefreshCw,
  Zap,
  Clock
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const PredictionPage: React.FC<{ symbol: string }> = ({ symbol }) => {
  const [horizon, setHorizon] = useState<number>(1);

  // Initial fetch for baseline data
  const { data: initialData, isLoading, error } = useQuery({
    queryKey: ['prediction', symbol, horizon],
    queryFn: () => api.getPrediction(symbol, horizon),
  });

  // WebSocket Live Continuous Streaming Hook
  const {
    livePrediction,
    connectionStatus,
    lastUpdatedSecondsAgo,
    streamMode,
    setStreamMode,
    priceDelta,
    priceDeltaPct,
    lastTickTimestamp,
    reconnect
  } = useLivePrediction(symbol, initialData || null);

  const isIndianStock = symbol.includes('.NS') || (!symbol.includes('.') && symbol.length > 4 && !['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'SPY', 'QQQ'].includes(symbol));
  const currPrefix = isIndianStock ? '₹' : '$';

  if (isLoading && !livePrediction) {
    return <LoadingSpinner message={`Initializing real-time prediction engine for ${symbol}...`} />;
  }

  if (error && !livePrediction) {
    return (
      <div className="card-surface p-6 text-rose-400">
        Failed to compute prediction for {symbol}. Make sure the dataset is available and models are initialized.
      </div>
    );
  }

  const activePrediction = livePrediction || initialData;
  if (!activePrediction) return null;

  const direction = activePrediction.predicted_direction || activePrediction.direction || 'UP';
  const isUp = direction === 'UP';
  const probUpPct = typeof activePrediction.probability_up_pct === 'number'
    ? activePrediction.probability_up_pct
    : (activePrediction.probability || 0.5) * 100;
  const confidencePct = typeof activePrediction.confidence_pct === 'number'
    ? activePrediction.confidence_pct
    : probUpPct;

  const expectedReturnPct = typeof activePrediction.expected_return_pct === 'number'
    ? activePrediction.expected_return_pct
    : (activePrediction.expected_return || 0) * 100;

  const modelName = activePrediction.model_metadata?.model_name || activePrediction.model_name || 'Ensemble Tree';
  const modelVersion = activePrediction.model_metadata?.model_version || 'v1.0';
  const riskLevel = activePrediction.risk_profile?.risk_level || activePrediction.risk_level || 'MEDIUM';
  const dailyVol = activePrediction.risk_profile?.daily_volatility || 0.015;
  const maxDrawdownPct = activePrediction.risk_profile?.max_drawdown_pct || 18.5;
  const annualizedVolPct = activePrediction.risk_profile?.annualized_volatility
    ? (activePrediction.risk_profile.annualized_volatility * 100).toFixed(1)
    : (dailyVol * Math.sqrt(252) * 100).toFixed(1);

  return (
    <div className="space-y-6">
      {/* Top Header & Live Streaming Status Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
              <span>{symbol} Real-Time Prediction & Reference Panel</span>
              <span className="text-xs font-mono font-normal text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/10">
                Live Inference
              </span>
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Continuously updated machine-learning directional inference, probability distributions, and ATR volatility bounds.
          </p>
        </div>

        {/* Live Stream Indicators & Mode Selector */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Stream Mode Switcher */}
          <div className="flex items-center space-x-1 bg-[#111827] p-1 rounded-xl border border-white/10 text-xs font-mono">
            <button
              onClick={() => setStreamMode('fast_demo')}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded-lg transition-all ${
                streamMode === 'fast_demo'
                  ? 'bg-blue-600 text-white shadow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Continuously updates model every 3.5 seconds on price ticks"
            >
              <Zap className="w-3 h-3 text-amber-300" />
              <span>Fast Live Ticks (3.5s)</span>
            </button>
            <button
              onClick={() => setStreamMode('live_market')}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded-lg transition-all ${
                streamMode === 'live_market'
                  ? 'bg-blue-600 text-white shadow-sm font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Polls live market feed every 15 seconds"
            >
              <Clock className="w-3 h-3 text-blue-300" />
              <span>Market Poller (15s)</span>
            </button>
          </div>

          {/* Connection Status Pill - §4 */}
          <div
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-xl border text-xs font-mono transition-all ${
              connectionStatus === 'LIVE'
                ? 'bg-emerald-950/30 text-emerald-300 border-emerald-500/30'
                : connectionStatus === 'CONNECTING'
                ? 'bg-amber-950/30 text-amber-300 border-amber-500/30'
                : connectionStatus === 'STALE'
                ? 'bg-amber-950/40 text-amber-300 border-amber-500/40'
                : 'bg-rose-950/40 text-rose-300 border-rose-500/40'
            }`}
          >
            {connectionStatus === 'LIVE' ? (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span>LIVE · Updated {lastUpdatedSecondsAgo}s ago</span>
              </>
            ) : connectionStatus === 'CONNECTING' ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-400" />
                <span>Connecting live stream...</span>
              </>
            ) : connectionStatus === 'STALE' ? (
              <>
                <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                <span>Last confirmed: {lastTickTimestamp || 'recently'}</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
                <span>Disconnected</span>
                <button
                  onClick={reconnect}
                  className="underline text-rose-300 hover:text-white ml-1 text-[11px]"
                >
                  Retry
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Hero Prediction Banner with Live Pulse Transitions */}
      <div
        className={`p-6 rounded-2xl border transition-all duration-300 shadow-2xl relative overflow-hidden ${
          isUp
            ? 'bg-gradient-to-r from-emerald-950/40 via-[#111827] to-[#111827] border-emerald-500/30 shadow-emerald-950/30'
            : 'bg-gradient-to-r from-rose-950/40 via-[#111827] to-[#111827] border-rose-500/30 shadow-rose-950/30'
        }`}
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
          {/* Main Direction & Probability */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 font-mono flex items-center space-x-1.5">
                <Radio className="w-3.5 h-3.5 text-blue-400 animate-pulse" />
                <span>Continuous Live Model Output</span>
              </span>
              {priceDelta !== 0 && (
                <span
                  className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                    priceDelta > 0
                      ? 'bg-emerald-500/20 text-emerald-300'
                      : 'bg-rose-500/20 text-rose-300'
                  }`}
                >
                  Tick: {priceDelta > 0 ? '+' : ''}{currPrefix}{priceDelta.toFixed(2)} ({priceDeltaPct > 0 ? '+' : ''}{priceDeltaPct}%)
                </span>
              )}
            </div>

            <div className="flex items-center space-x-3">
              <div
                className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-transform duration-300 ${
                  isUp
                    ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-inner'
                    : 'bg-rose-500/20 text-rose-400 border border-rose-500/40 shadow-inner'
                }`}
              >
                {isUp ? <TrendingUp className="w-8 h-8" /> : <TrendingDown className="w-8 h-8" />}
              </div>
              <div>
                <span
                  className={`text-3xl font-extrabold tracking-tight font-mono transition-colors duration-300 ${
                    isUp ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {direction}
                </span>
                <span className="text-xs text-slate-400 block">
                  Calibrated Probability: <strong className="text-white font-mono">{probUpPct.toFixed(1)}%</strong>
                </span>
              </div>
            </div>
          </div>

          {/* Probability Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-rose-400">DOWN ({(100 - probUpPct).toFixed(1)}%)</span>
              <span className="text-emerald-400">UP ({probUpPct.toFixed(1)}%)</span>
            </div>
            <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden flex border border-white/10">
              <div
                className="bg-rose-500 transition-all duration-300 ease-out"
                style={{ width: `${Math.max(0, 100 - probUpPct)}%` }}
              />
              <div
                className="bg-emerald-500 transition-all duration-300 ease-out"
                style={{ width: `${Math.min(100, probUpPct)}%` }}
              />
            </div>
            <p className="text-[11px] text-slate-400 text-center">
              Re-computed continuously on price ticks using rolling momentum & Parkinson dispersion
            </p>
          </div>

          {/* Risk Level Badge */}
          <div className="flex flex-col md:items-end justify-center space-y-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 font-mono">
              Risk Profile
            </span>
            <span
              className={`px-4 py-1.5 rounded-xl text-sm font-bold font-mono border ${
                riskLevel === 'LOW'
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : riskLevel === 'MEDIUM'
                  ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
              }`}
            >
              {riskLevel} RISK
            </span>
            <span className="text-[11px] text-slate-400 font-mono">
              Annualized Vol: {annualizedVolPct}%
            </span>
          </div>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Live Expected Return"
          value={`${expectedReturnPct >= 0 ? '+' : ''}${expectedReturnPct.toFixed(2)}%`}
          subtext="Model regression expectation"
          trend={expectedReturnPct >= 0 ? 'positive' : 'negative'}
        />
        <KpiCard
          label="Model Architecture"
          value={modelName}
          subtext={`Version: ${modelVersion}`}
          icon={<Cpu className="w-5 h-5" />}
        />
        <KpiCard
          label="Max Historical Drawdown"
          value={`${maxDrawdownPct.toFixed(1)}%`}
          subtext="Worst peak-to-trough drop"
          trend="negative"
        />
        <KpiCard
          label="Live Price Basis"
          value={`${currPrefix}${(activePrediction.current_price || 0).toFixed(2)}`}
          subtext={`Updated at ${lastTickTimestamp || 'Latest'}`}
          icon={<Activity className="w-5 h-5" />}
        />
      </div>

      {/* Model-Derived Educational Reference Panel (Strict Framing Rules 1-5, Live Synchronized) */}
      <ModelReferencePanel
        symbol={symbol}
        currency={isIndianStock ? 'INR' : 'USD'}
        referenceData={activePrediction.reference_levels}
        currentPrice={activePrediction.current_price}
      />

      {/* Bottom Guardrails and Explanations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card-surface p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Continuous Live Inference Architecture</h3>
            <Link
              to="/explainability"
              className="text-xs text-blue-400 hover:text-blue-300 font-medium"
            >
              View SHAP Waterfall &rarr;
            </Link>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed font-sans">
            The live streaming engine registers actively viewed ticker subscriptions over WebSockets. When live price ticks arrive or candles close, the inference pipeline updates the latest feature vector and evaluates tree ensemble weights in sub-second time without disk bottlenecks.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono text-slate-400">
            <div className="p-3 rounded-lg bg-[#0B0F17] border border-white/5 space-y-1">
              <span className="text-white font-semibold block">Inference Cadence:</span>
              <span>Re-evaluates every tick / bar update</span>
            </div>
            <div className="p-3 rounded-lg bg-[#0B0F17] border border-white/5 space-y-1">
              <span className="text-white font-semibold block">Zero Lookahead:</span>
              <span>Uses strictly closed historical + latest live tick</span>
            </div>
          </div>
        </div>

        {/* Prediction Guardrails Card */}
        <div className="card-surface p-5 space-y-4">
          <div className="flex items-center space-x-2 text-amber-400">
            <AlertCircle className="w-5 h-5" />
            <h3 className="text-sm font-semibold text-white">Platform Guardrails</h3>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            MarketMind is an academic research platform. Real-time model updates demonstrate online statistical adaptation and volatility bounds.
          </p>
          <div className="space-y-2 text-xs text-slate-400 font-mono">
            <div className="p-2 rounded bg-[#0B0F17] border border-white/5">
              Live updates scoped strictly to active view
            </div>
            <div className="p-2 rounded bg-[#0B0F17] border border-white/5">
              Educational reference levels with visible multipliers
            </div>
            <div className="p-2 rounded bg-[#0B0F17] border border-white/5">
              Zero automated trading signals
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
