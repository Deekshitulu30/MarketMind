import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../services/api';
import { PcaScatterChart } from '../charts/PcaScatterChart';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { KpiCard } from '../components/KpiCard';
import {
  Layers,
  Play,
  CheckCircle,
  Award,
  Cpu,
  BarChart,
  PieChart,
} from 'lucide-react';

export const ModelLab: React.FC<{ symbol: string }> = ({ symbol }) => {
  const queryClient = useQueryClient();
  const [trainRatio, setTrainRatio] = useState(0.70);

  const { data: comparison, isLoading: isComparisonLoading } = useQuery({
    queryKey: ['models-comparison', symbol],
    queryFn: () => api.getModelsComparison(symbol),
  });

  const { data: regimes, isLoading: isRegimesLoading } = useQuery({
    queryKey: ['market-regimes', symbol],
    queryFn: () => api.getMarketRegimes(symbol),
  });

  const trainMutation = useMutation({
    mutationFn: () => api.trainModels({ symbol, train_ratio: trainRatio }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models-comparison', symbol] });
      queryClient.invalidateQueries({ queryKey: ['market-regimes', symbol] });
      queryClient.invalidateQueries({ queryKey: ['prediction', symbol] });
    },
  });

  if (isComparisonLoading || isRegimesLoading) {
    return <LoadingSpinner message={`Loading model evaluation matrix for ${symbol}...`} />;
  }

  const models = comparison?.models || [];
  const bestModel = models.find((m) => m.is_best_model) || models[0];

  return (
    <div className="space-y-6">
      {/* Header & Retrain Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <span>{symbol} Machine Learning & Regime Lab</span>
            <span className="text-xs font-mono font-normal text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/10">
              Benchmark & Selection
            </span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Chronologically trained classification and regression algorithms compared against naive baselines.
          </p>
        </div>

        {/* Retrain Button */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => trainMutation.mutate()}
            disabled={trainMutation.isPending}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-blue-500/20 transition-all disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{trainMutation.isPending ? 'Training Algorithms...' : 'Retrain All Models'}</span>
          </button>
        </div>
      </div>

      {/* Top Model KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Champion Model"
          value={bestModel?.model_name || 'Random Forest'}
          subtext="Selected by out-of-sample F1 / AUC"
          icon={<Award className="w-5 h-5 text-amber-400" />}
          trend="positive"
        />
        <KpiCard
          label="Test Accuracy"
          value={bestModel?.test_accuracy ? `${(bestModel.test_accuracy * 100).toFixed(1)}%` : 'N/A'}
          subtext="Chronological holdout split"
          trend="positive"
        />
        <KpiCard
          label="ROC-AUC Score"
          value={bestModel?.test_roc_auc ? bestModel.test_roc_auc.toFixed(3) : 'N/A'}
          subtext="Discriminative power"
          trend="positive"
        />
        <KpiCard
          label="Regime Clusters"
          value={regimes?.n_clusters || 4}
          subtext="K-Means Market States"
          icon={<PieChart className="w-5 h-5" />}
        />
      </div>

      {/* Model Benchmark Comparison Table */}
      <div className="card-surface p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Algorithm Benchmark Leaderboard</h3>
            <p className="text-xs text-slate-400">
              Evaluated strictly on chronological out-of-sample data points
            </p>
          </div>
          <span className="text-xs font-mono text-slate-400">
            {models.length} Models Benchmarked
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-white/5 text-slate-400 uppercase text-[10px]">
                <th className="pb-3">Algorithm</th>
                <th className="pb-3">Task Type</th>
                <th className="pb-3 text-right">Val Acc / R²</th>
                <th className="pb-3 text-right">Test Acc</th>
                <th className="pb-3 text-right">F1 Score</th>
                <th className="pb-3 text-right">ROC-AUC</th>
                <th className="pb-3 text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {models.map((m) => (
                <tr
                  key={m.id}
                  className={`hover:bg-white/5 transition-colors ${
                    m.is_best_model ? 'bg-blue-500/10' : ''
                  }`}
                >
                  <td className="py-3 font-semibold text-slate-200 flex items-center space-x-2">
                    {m.is_best_model && <Award className="w-3.5 h-3.5 text-amber-400" />}
                    <span>{m.model_name}</span>
                  </td>
                  <td className="py-3 text-slate-400 uppercase text-[11px] font-sans">
                    {m.task_type}
                  </td>
                  <td className="py-3 text-right text-slate-300">
                    {m.validation_metrics?.accuracy
                      ? `${(m.validation_metrics.accuracy * 100).toFixed(1)}%`
                      : m.validation_metrics?.r_squared !== undefined
                      ? m.validation_metrics.r_squared.toFixed(3)
                      : 'N/A'}
                  </td>
                  <td className="py-3 text-right text-slate-100 font-bold">
                    {m.test_accuracy ? `${(m.test_accuracy * 100).toFixed(1)}%` : 'N/A'}
                  </td>
                  <td className="py-3 text-right text-slate-300">
                    {m.test_f1_score ? m.test_f1_score.toFixed(3) : 'N/A'}
                  </td>
                  <td className="py-3 text-right text-slate-300">
                    {m.test_roc_auc ? m.test_roc_auc.toFixed(3) : 'N/A'}
                  </td>
                  <td className="py-3 text-center font-sans">
                    {m.is_best_model ? (
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                        Champion
                      </span>
                    ) : (
                      <span className="text-slate-500 text-[11px]">Candidate</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Unsupervised Learning: Market Regimes & PCA */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* K-Means Market Regimes Card */}
        {regimes && (
          <div className="card-surface p-5 space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Unsupervised Market Regimes (K-Means)</h3>
              <p className="text-xs text-slate-400">
                Clustering price action into 4 latent macroeconomic volatility states
              </p>
            </div>

            <div className="space-y-3 font-mono text-xs">
              {regimes.regimes.map((regime) => (
                <div
                  key={regime.cluster_id}
                  className="p-3 rounded-lg bg-[#0B0F17] border border-white/5 space-y-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-blue-400">{regime.regime_name}</span>
                    <span className="text-slate-400 text-[11px]">
                      {regime.sample_count} trading sessions
                    </span>
                  </div>
                  <div className="flex justify-between text-[11px] text-slate-400">
                    <span>Mean Return: <strong className="text-slate-200">{(regime.mean_return * 100).toFixed(2)}%</strong></span>
                    <span>Volatility: <strong className="text-slate-200">{(regime.mean_volatility * 100).toFixed(1)}%</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* PCA Projection Chart */}
        {regimes && (
          <PcaScatterChart
            points={regimes.pca_points}
            explainedVarianceRatio={regimes.explained_variance_ratio}
          />
        )}
      </div>
    </div>
  );
};
