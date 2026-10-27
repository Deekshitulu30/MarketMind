import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { ReturnDistributionChart } from '../charts/ReturnDistributionChart';
import { CorrelationHeatmap } from '../charts/CorrelationHeatmap';
import { BivariateScatterChart } from '../charts/BivariateScatterChart';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { KpiCard } from '../components/KpiCard';
import { HelpCircle, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';

export const StatisticsLab: React.FC<{ symbol: string }> = ({ symbol }) => {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['statistics', symbol],
    queryFn: () => api.getStatistics(symbol),
  });

  if (isLoading) return <LoadingSpinner message={`Running quantitative statistical analysis on ${symbol}...`} />;
  if (error || !stats) {
    return (
      <div className="card-surface p-6 text-rose-400">
        Failed to compute statistics for {symbol}.
      </div>
    );
  }

  const descriptive = stats?.descriptive || stats?.return_summary || {};
  const distribution = stats?.distribution || stats?.distribution_analysis || {};
  const correlation = stats?.correlation || {
    columns: stats?.correlation_matrix?.columns || [],
    pearson_matrix: stats?.correlation_matrix?.pearson_matrix || [],
    spearman_matrix: stats?.correlation_matrix?.spearman_matrix || [],
    bivariate_regressions: stats?.bivariate_regressions || {}
  };
  const hypothesis_test = stats?.hypothesis_test || {};

  const var95 = typeof distribution?.var_95 === 'number'
    ? distribution.var_95
    : (typeof distribution?.var_95_historical === 'number' ? distribution.var_95_historical : 0.02);
  const var99 = typeof distribution?.var_99 === 'number'
    ? distribution.var_99
    : (typeof distribution?.var_99_historical === 'number' ? distribution.var_99_historical : 0.035);
  const skewness = typeof descriptive?.skewness === 'number' ? descriptive.skewness : 0.0;
  const kurtosis = typeof descriptive?.kurtosis === 'number' ? descriptive.kurtosis : 0.0;
  const sampleSize = distribution?.sample_size || stats?.period?.total_trading_days || 0;
  const meanRet = typeof distribution?.mean_return === 'number'
    ? distribution.mean_return
    : (typeof distribution?.mean_daily_return === 'number' ? distribution.mean_daily_return : 0.0);
  const stdRet = typeof distribution?.std_return === 'number'
    ? distribution.std_return
    : (typeof distribution?.std_daily_return === 'number' ? distribution.std_daily_return : 0.015);
  const meanLogRet = typeof distribution?.mean_log_return === 'number' ? distribution.mean_log_return : meanRet;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
          <span>{symbol} Quantitative Statistics & Probability Lab</span>
          <span className="text-xs font-mono font-normal text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/10">
            Rigorous Mathematical Suite
          </span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Moments, parametric & empirical probability densities, Value-at-Risk (VaR), correlation structure, and formal hypothesis tests.
        </p>
      </div>

      {/* KPI Cards: VaR & Skew/Kurtosis */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Value-at-Risk (95% Daily)"
          value={`${(var95 * 100).toFixed(2)}%`}
          subtext="Maximum daily loss at 95% confidence"
          trend="negative"
        />
        <KpiCard
          label="Value-at-Risk (99% Daily)"
          value={`${(var99 * 100).toFixed(2)}%`}
          subtext="Maximum daily loss at 99% confidence"
          trend="negative"
        />
        <KpiCard
          label="Distribution Skewness"
          value={skewness.toFixed(3)}
          subtext={skewness < 0 ? 'Negative (Left tail risk)' : 'Positive (Right tail)'}
          trend={skewness < 0 ? 'negative' : 'positive'}
        />
        <KpiCard
          label="Excess Kurtosis"
          value={kurtosis.toFixed(3)}
          subtext={kurtosis > 0 ? 'Heavy-tailed (Leptokurtic)' : 'Thin-tailed'}
          trend="neutral"
        />
      </div>

      {/* Distribution Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ReturnDistributionChart distribution={distribution} symbol={symbol} />
        </div>

        {/* Probability Insights Card */}
        <div className="card-surface p-5 space-y-4">
          <h3 className="text-sm font-semibold text-white">Probability Characteristics</h3>
          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between p-2 rounded bg-[#0B0F17] border border-white/5">
              <span className="text-slate-400">Sample Size (N):</span>
              <span className="text-slate-200">{sampleSize} days</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-[#0B0F17] border border-white/5">
              <span className="text-slate-400">Mean Daily Return:</span>
              <span className="text-slate-200 font-bold">{(meanRet * 100).toFixed(4)}%</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-[#0B0F17] border border-white/5">
              <span className="text-slate-400">Daily Return Std Dev:</span>
              <span className="text-slate-200 font-bold">{(stdRet * 100).toFixed(4)}%</span>
            </div>
            <div className="flex justify-between p-2 rounded bg-[#0B0F17] border border-white/5">
              <span className="text-slate-400">Mean Log Return:</span>
              <span className="text-slate-200">{(meanLogRet * 100).toFixed(4)}%</span>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-xs text-slate-300">
            <p className="font-semibold text-blue-400 mb-1">Financial Note:</p>
            Asset returns often deviate from pure Gaussian normality due to volatility clustering and fat-tail event frequency.
          </div>
        </div>
      </div>

      {/* Correlation Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CorrelationHeatmap
          columns={correlation.columns}
          pearsonMatrix={correlation.pearson_matrix}
          spearmanMatrix={correlation.spearman_matrix}
        />

        {correlation.bivariate_regressions?.return_vs_market && (
          <BivariateScatterChart
            title="OLS Regression: Asset Return vs Market Return (SPY)"
            xLabel="Market Return (SPY)"
            yLabel={`${symbol} Return`}
            slope={correlation.bivariate_regressions.return_vs_market.slope}
            intercept={correlation.bivariate_regressions.return_vs_market.intercept}
            rSquared={correlation.bivariate_regressions.return_vs_market.r_squared}
            pValue={correlation.bivariate_regressions.return_vs_market.p_value}
            scatterPoints={correlation.bivariate_regressions.return_vs_market.scatter_points}
            regressionLine={correlation.bivariate_regressions.return_vs_market.regression_line}
          />
        )}
      </div>

      {/* Formal Hypothesis Testing Card */}
      <div className="card-surface p-6 space-y-4 border-l-4 border-l-blue-500">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <HelpCircle className="w-5 h-5 text-blue-400" />
            <h3 className="text-base font-bold text-white">
              Hypothesis Test: {hypothesis_test.test_name}
            </h3>
          </div>
          <span
            className={`px-3 py-1 rounded-full text-xs font-mono font-semibold flex items-center space-x-1.5 ${
              hypothesis_test.reject_null
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
            }`}
          >
            {hypothesis_test.reject_null ? (
              <CheckCircle2 className="w-3.5 h-3.5" />
            ) : (
              <XCircle className="w-3.5 h-3.5" />
            )}
            <span>{hypothesis_test.reject_null ? 'Reject H₀' : 'Fail to Reject H₀'}</span>
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs bg-[#0B0F17] p-4 rounded-lg border border-white/5">
          <div className="space-y-1.5">
            <p className="text-slate-400">
              <strong className="text-slate-300">Null Hypothesis (H₀):</strong> {hypothesis_test.null_hypothesis}
            </p>
            <p className="text-slate-400">
              <strong className="text-slate-300">Alternative (H₁):</strong> {hypothesis_test.alternative_hypothesis}
            </p>
          </div>
          <div className="space-y-1.5">
            <p className="text-slate-400">
              <strong className="text-slate-300">t-statistic:</strong> {typeof hypothesis_test?.statistic === 'number' ? hypothesis_test.statistic.toFixed(4) : 'N/A'}
            </p>
            <p className="text-slate-400">
              <strong className="text-slate-300">p-value:</strong>{' '}
              <span className={typeof hypothesis_test?.p_value === 'number' && hypothesis_test.p_value < 0.05 ? 'text-emerald-400 font-bold' : 'text-slate-300'}>
                {typeof hypothesis_test?.p_value === 'number' ? (hypothesis_test.p_value < 0.0001 ? '< 0.0001' : hypothesis_test.p_value.toFixed(4)) : 'N/A'}
              </span>{' '}
              (α = {hypothesis_test?.alpha ?? 0.05})
            </p>
          </div>
        </div>

        <p className="text-xs text-slate-300 bg-white/5 p-3 rounded border border-white/5">
          <strong>Interpretation:</strong> {hypothesis_test.interpretation}
        </p>
      </div>
    </div>
  );
};
