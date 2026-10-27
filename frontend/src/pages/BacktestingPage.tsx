import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { BacktestEquityChart } from '../charts/BacktestEquityChart';
import { ConfusionMatrixCard } from '../charts/ConfusionMatrixCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { KpiCard } from '../components/KpiCard';
import { History, Play, CheckCircle2, TrendingUp, ShieldCheck, Activity } from 'lucide-react';

export const BacktestingPage: React.FC<{ symbol: string }> = ({ symbol }) => {
  const queryClient = useQueryClient();
  const [modelName, setModelName] = useState('Random Forest Classifier');
  const [nFolds, setNFolds] = useState(3);

  const { data: backtest, isLoading } = useQuery({
    queryKey: ['backtest', symbol, modelName, nFolds],
    queryFn: () => api.runBacktest({ symbol, model_name: modelName, n_folds: nFolds }),
  });

  const runMutation = useMutation({
    mutationFn: () => api.runBacktest({ symbol, model_name: modelName, n_folds: nFolds }),
    onSuccess: (data) => {
      queryClient.setQueryData(['backtest', symbol, modelName, nFolds], data);
    },
  });

  if (isLoading) {
    return <LoadingSpinner message={`Running walk-forward chronological backtest on ${symbol}...`} />;
  }

  if (!backtest) {
    return (
      <div className="card-surface p-6 text-rose-400">
        Failed to execute backtest. Ensure sufficient price history exists.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <span>{symbol} Walk-Forward Backtesting Lab</span>
            <span className="text-xs font-mono font-normal text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/10">
              Expanding Window Cross-Validation
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Evaluating historical predictive reliability without future information leakage.
          </p>
        </div>

        {/* Model & Fold Selectors */}
        <div className="flex items-center space-x-3">
          <select
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            className="bg-[#111827] text-slate-200 text-xs px-3 py-2 rounded-lg border border-white/10 font-mono"
          >
            <option value="Random Forest Classifier">Random Forest</option>
            <option value="Logistic Regression">Logistic Regression</option>
            <option value="Support Vector Classifier">SVM Classifier</option>
            <option value="Decision Tree Classifier">Decision Tree</option>
          </select>

          <select
            value={nFolds}
            onChange={(e) => setNFolds(Number(e.target.value))}
            className="bg-[#111827] text-slate-200 text-xs px-3 py-2 rounded-lg border border-white/10 font-mono"
          >
            <option value={2}>2 Walk-Forward Folds</option>
            <option value={3}>3 Walk-Forward Folds</option>
            <option value={4}>4 Walk-Forward Folds</option>
            <option value={5}>5 Walk-Forward Folds</option>
          </select>

          <button
            onClick={() => runMutation.mutate()}
            disabled={runMutation.isPending}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-blue-500/20 transition-all disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{runMutation.isPending ? 'Simulating...' : 'Run Simulation'}</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Out-of-Sample Accuracy"
          value={`${(backtest.mean_accuracy * 100).toFixed(1)}%`}
          subtext={`Across ${backtest.n_folds} chronological folds`}
          trend={backtest.mean_accuracy > 0.50 ? 'positive' : 'negative'}
        />
        <KpiCard
          label="Strategy Cumulative Return"
          value={`${(backtest.cumulative_strategy_return_pct || 0).toFixed(2)}%`}
          subtext={`vs Benchmark: ${(backtest.cumulative_benchmark_return_pct || 0).toFixed(2)}%`}
          trend={backtest.cumulative_strategy_return_pct >= 0 ? 'positive' : 'negative'}
        />
        <KpiCard
          label="Annualized Sharpe Ratio"
          value={backtest.sharpe_ratio ? backtest.sharpe_ratio.toFixed(2) : '0.00'}
          subtext="Risk-adjusted return"
          trend={backtest.sharpe_ratio && backtest.sharpe_ratio > 1 ? 'positive' : 'neutral'}
        />
        <KpiCard
          label="Strategy Max Drawdown"
          value={`${(backtest.max_drawdown_pct || 0).toFixed(1)}%`}
          subtext="Peak-to-trough worst decline"
          trend="negative"
        />
      </div>

      {/* Equity Chart & Confusion Matrix */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <BacktestEquityChart series={backtest.equity_curve || []} />
        </div>

        <div>
          <ConfusionMatrixCard matrix={backtest.overall_confusion_matrix} />
        </div>
      </div>

      {/* Per-Fold Expanding Window Table */}
      <div className="card-surface p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">Chronological Walk-Forward Folds</h3>
          <span className="text-xs font-mono text-slate-400">
            Training set expands forward; test set is strictly unseen
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-white/5 text-slate-400 uppercase text-[10px]">
                <th className="pb-3">Fold</th>
                <th className="pb-3">Train Period</th>
                <th className="pb-3">Out-of-Sample Test Period</th>
                <th className="pb-3 text-right">Test Size</th>
                <th className="pb-3 text-right">Accuracy</th>
                <th className="pb-3 text-right">Strategy Return</th>
                <th className="pb-3 text-right">Benchmark Return</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {backtest.folds.map((fold) => (
                <tr key={fold.fold} className="hover:bg-white/5 transition-colors">
                  <td className="py-3 font-bold text-blue-400">Fold #{fold.fold}</td>
                  <td className="py-3 text-slate-300">
                    {fold.train_start} &rarr; {fold.train_end}
                  </td>
                  <td className="py-3 text-slate-300">
                    {fold.test_start} &rarr; {fold.test_end}
                  </td>
                  <td className="py-3 text-right text-slate-400">{fold.test_samples}</td>
                  <td className="py-3 text-right text-slate-100 font-bold">
                    {(fold.accuracy * 100).toFixed(1)}%
                  </td>
                  <td className="py-3 text-right text-emerald-400 font-semibold">
                    {(fold.strategy_return_pct || 0).toFixed(2)}%
                  </td>
                  <td className="py-3 text-right text-slate-400">
                    {(fold.benchmark_return_pct || 0).toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
