import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '../services/api';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { KpiCard } from '../components/KpiCard';
import {
  Sliders,
  TrendingUp,
  TrendingDown,
  RotateCcw,
  Sparkles,
  Zap,
  ShieldAlert,
  ArrowRight,
  Flame,
} from 'lucide-react';

export const WhatIfSimulatorPage: React.FC<{ symbol: string }> = ({ symbol }) => {
  const [marketDelta, setMarketDelta] = useState<number>(0.0);
  const [volumeDelta, setVolumeDelta] = useState<number>(0.0);
  const [volatilityDelta, setVolatilityDelta] = useState<number>(0.0);
  const [momentumDelta, setMomentumDelta] = useState<number>(0.0);

  const { data: simulation, isLoading, refetch } = useQuery({
    queryKey: ['what-if', symbol, marketDelta, volumeDelta, volatilityDelta, momentumDelta],
    queryFn: () =>
      api.runWhatIf({
        symbol,
        market_return_delta: marketDelta,
        volume_delta_pct: volumeDelta,
        volatility_delta_pct: volatilityDelta,
        momentum_delta_pct: momentumDelta,
      }),
  });

  const handlePreset = (market: number, vol: number, volatility: number, mom: number) => {
    setMarketDelta(market);
    setVolumeDelta(vol);
    setVolatilityDelta(volatility);
    setMomentumDelta(mom);
  };

  if (isLoading && !simulation) {
    return <LoadingSpinner message={`Running stress-testing simulation on ${symbol}...`} />;
  }

  const baseline = simulation?.baseline_outcome;
  const scenario = simulation?.scenario_outcome;
  const delta = simulation?.delta_shifts;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <span>{symbol} Hypothetical What-If & Stress-Testing Sandbox</span>
            <span className="text-xs font-mono font-normal text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/10">
              Counterfactual Inference
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Perturb macroeconomic conditions and technical signals to evaluate prediction sensitivity against a frozen baseline.
          </p>
        </div>

        {/* Reset Button */}
        <button
          onClick={() => handlePreset(0.0, 0.0, 0.0, 0.0)}
          className="flex items-center space-x-2 px-3 py-1.5 bg-[#111827] hover:bg-white/5 text-slate-300 rounded-lg text-xs font-mono border border-white/10 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset Baseline</span>
        </button>
      </div>

      {/* Preset Buttons */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider mr-2">
          Scenarios:
        </span>
        <button
          onClick={() => handlePreset(-0.05, 0.40, 0.50, -0.30)}
          className="px-3 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 rounded-lg text-xs font-medium border border-rose-500/20 transition-all flex items-center space-x-1.5"
        >
          <Flame className="w-3.5 h-3.5" />
          <span>Flash Crash (-5% SPY, +50% Vol)</span>
        </button>
        <button
          onClick={() => handlePreset(0.03, 0.25, -0.20, 0.35)}
          className="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 rounded-lg text-xs font-medium border border-emerald-500/20 transition-all flex items-center space-x-1.5"
        >
          <Zap className="w-3.5 h-3.5" />
          <span>Bull Breakout (+3% SPY, +35% Mom)</span>
        </button>
        <button
          onClick={() => handlePreset(-0.02, -0.40, -0.30, -0.10)}
          className="px-3 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 rounded-lg text-xs font-medium border border-amber-500/20 transition-all flex items-center space-x-1.5"
        >
          <ShieldAlert className="w-3.5 h-3.5" />
          <span>Liquidity Crunch (-40% Vol, -2% SPY)</span>
        </button>
      </div>

      {/* Interactive Parameter Sliders Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 card-surface p-5">
        {/* Slider 1: Market Return Delta */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-400">Market Return Δ (SPY):</span>
            <span className={marketDelta >= 0 ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
              {marketDelta > 0 ? `+${(marketDelta * 100).toFixed(1)}%` : `${(marketDelta * 100).toFixed(1)}%`}
            </span>
          </div>
          <input
            type="range"
            min="-0.15"
            max="0.15"
            step="0.01"
            value={marketDelta}
            onChange={(e) => setMarketDelta(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
          <div className="flex justify-between text-[10px] text-slate-400 font-mono">
            <span>-15%</span>
            <span>0%</span>
            <span>+15%</span>
          </div>
        </div>

        {/* Slider 2: Volume Delta */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-400">Volume Surge Δ:</span>
            <span className={volumeDelta >= 0 ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
              {volumeDelta > 0 ? `+${(volumeDelta * 100).toFixed(0)}%` : `${(volumeDelta * 100).toFixed(0)}%`}
            </span>
          </div>
          <input
            type="range"
            min="-0.80"
            max="0.80"
            step="0.05"
            value={volumeDelta}
            onChange={(e) => setVolumeDelta(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          />
          <div className="flex justify-between text-[10px] text-slate-400 font-mono">
            <span>-80%</span>
            <span>0%</span>
            <span>+80%</span>
          </div>
        </div>

        {/* Slider 3: Volatility Delta */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-400">Volatility Shock Δ:</span>
            <span className={volatilityDelta >= 0 ? 'text-amber-400 font-bold' : 'text-blue-400 font-bold'}>
              {volatilityDelta > 0 ? `+${(volatilityDelta * 100).toFixed(0)}%` : `${(volatilityDelta * 100).toFixed(0)}%`}
            </span>
          </div>
          <input
            type="range"
            min="-0.80"
            max="0.80"
            step="0.05"
            value={volatilityDelta}
            onChange={(e) => setVolatilityDelta(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
          />
          <div className="flex justify-between text-[10px] text-slate-400 font-mono">
            <span>-80%</span>
            <span>0%</span>
            <span>+80%</span>
          </div>
        </div>

        {/* Slider 4: Momentum Delta */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-400">Price Momentum Δ:</span>
            <span className={momentumDelta >= 0 ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
              {momentumDelta > 0 ? `+${(momentumDelta * 100).toFixed(0)}%` : `${(momentumDelta * 100).toFixed(0)}%`}
            </span>
          </div>
          <input
            type="range"
            min="-0.80"
            max="0.80"
            step="0.05"
            value={momentumDelta}
            onChange={(e) => setMomentumDelta(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
          />
          <div className="flex justify-between text-[10px] text-slate-400 font-mono">
            <span>-80%</span>
            <span>0%</span>
            <span>+80%</span>
          </div>
        </div>
      </div>

      {/* Comparative Side-by-Side Results */}
      {baseline && scenario && delta && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
          {/* Baseline Outcome Card */}
          <div className="card-surface p-6 space-y-4 border-slate-700/60 flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 font-mono block mb-1">
                Frozen Actual Baseline
              </span>
              <h3 className="text-lg font-bold text-slate-200">Historical Feature State</h3>
              <p className="text-xs text-slate-400">Cutoff Date: {simulation.data_cutoff_date}</p>
            </div>

            <div className="space-y-3 font-mono text-xs my-4">
              <div className="flex justify-between p-2.5 rounded bg-[#0B0F17] border border-white/5">
                <span className="text-slate-400">Direction:</span>
                <span className={`font-bold ${baseline.direction === 'UP' ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {baseline.direction}
                </span>
              </div>
              <div className="flex justify-between p-2.5 rounded bg-[#0B0F17] border border-white/5">
                <span className="text-slate-400">Probability UP:</span>
                <span className="text-slate-100 font-bold">{(baseline.probability * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between p-2.5 rounded bg-[#0B0F17] border border-white/5">
                <span className="text-slate-400">Expected Return:</span>
                <span className="text-slate-100 font-bold">{((baseline.expected_return || 0) * 100).toFixed(2)}%</span>
              </div>
              <div className="flex justify-between p-2.5 rounded bg-[#0B0F17] border border-white/5">
                <span className="text-slate-400">Risk Assessment:</span>
                <span className="text-amber-400 font-bold">{baseline.risk_level} RISK</span>
              </div>
            </div>

            <div className="text-[11px] text-slate-500 text-center font-mono">
              Unmodified actual market closing state
            </div>
          </div>

          {/* Delta Shift Indicator Card */}
          <div className="card-surface p-6 bg-gradient-to-b from-blue-950/20 via-[#111827] to-[#111827] border-blue-500/30 flex flex-col justify-between text-center space-y-4">
            <div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-blue-400 font-mono block mb-1">
                Net Delta Shift
              </span>
              <h3 className="text-lg font-bold text-white">Model Sensitivity</h3>
            </div>

            <div className="space-y-4 my-2">
              <div>
                <span className="text-xs text-slate-400 block font-mono">Probability Shift</span>
                <span
                  className={`text-3xl font-extrabold font-mono ${
                    delta.probability_delta >= 0 ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {delta.probability_delta > 0 ? `+${(delta.probability_delta * 100).toFixed(1)}%` : `${(delta.probability_delta * 100).toFixed(1)}%`}
                </span>
              </div>

              <div>
                <span className="text-xs text-slate-400 block font-mono">Expected Return Shift</span>
                <span
                  className={`text-2xl font-bold font-mono ${
                    delta.expected_return_delta >= 0 ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {delta.expected_return_delta > 0 ? `+${(delta.expected_return_delta * 100).toFixed(2)}%` : `${(delta.expected_return_delta * 100).toFixed(2)}%`}
                </span>
              </div>

              <div className="text-xs font-mono text-slate-300">
                Direction Flipped: <strong className={delta.direction_flipped ? 'text-amber-400' : 'text-slate-400'}>{delta.direction_flipped ? 'YES' : 'NO'}</strong>
              </div>
            </div>

            <div className="text-[11px] text-slate-400 bg-blue-500/10 p-2 rounded border border-blue-500/20">
              Evaluated using frozen {simulation.model_name}
            </div>
          </div>

          {/* Perturbed Scenario Outcome Card */}
          <div
            className={`card-surface p-6 space-y-4 flex flex-col justify-between border ${
              scenario.direction === 'UP'
                ? 'border-emerald-500/40 bg-gradient-to-b from-emerald-950/20 via-[#111827] to-[#111827]'
                : 'border-rose-500/40 bg-gradient-to-b from-rose-950/20 via-[#111827] to-[#111827]'
            }`}
          >
            <div>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 font-mono block mb-1">
                Counterfactual Scenario
              </span>
              <h3 className="text-lg font-bold text-white">Perturbed Outcome</h3>
              <p className="text-xs text-slate-400">Simulated response</p>
            </div>

            <div className="space-y-3 font-mono text-xs my-4">
              <div className="flex justify-between p-2.5 rounded bg-[#0B0F17] border border-white/5">
                <span className="text-slate-400">Predicted Direction:</span>
                <span className={`font-bold ${scenario.direction === 'UP' ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {scenario.direction}
                </span>
              </div>
              <div className="flex justify-between p-2.5 rounded bg-[#0B0F17] border border-white/5">
                <span className="text-slate-400">Probability UP:</span>
                <span className="text-white font-bold">{(scenario.probability * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between p-2.5 rounded bg-[#0B0F17] border border-white/5">
                <span className="text-slate-400">Expected Return:</span>
                <span className="text-white font-bold">{((scenario.expected_return || 0) * 100).toFixed(2)}%</span>
              </div>
              <div className="flex justify-between p-2.5 rounded bg-[#0B0F17] border border-white/5">
                <span className="text-slate-400">Scenario Risk:</span>
                <span className="text-amber-400 font-bold">{scenario.risk_level} RISK</span>
              </div>
            </div>

            <div className="text-[11px] text-slate-400 text-center font-mono">
              Hypothetical inference based on user perturbation
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
