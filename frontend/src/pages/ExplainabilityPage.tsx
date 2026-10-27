import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { ShapWaterfallChart } from '../charts/ShapWaterfallChart';
import { PartialDependenceChart } from '../charts/PartialDependenceChart';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { KpiCard } from '../components/KpiCard';
import { Info, Sparkles, Sliders, CheckCircle2 } from 'lucide-react';
import Plot from 'react-plotly.js';

export const ExplainabilityPage: React.FC<{ symbol: string }> = ({ symbol }) => {
  const { data: explain, isLoading, error } = useQuery({
    queryKey: ['explainability', symbol],
    queryFn: () => api.getExplanation(symbol),
  });

  if (isLoading) {
    return <LoadingSpinner message={`Computing Shapley values and partial dependence curves for ${symbol}...`} />;
  }

  if (error || !explain) {
    return (
      <div className="card-surface p-6 text-rose-400">
        Failed to compute explainability data. Ensure models are trained in Model Lab.
      </div>
    );
  }

  const globalFeats = explain.global_importance || [];
  const topGlobalLabels = globalFeats.map((f) => f.feature);
  const topGlobalWeights = globalFeats.map((f) => f.importance_weight);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
          <span>{symbol} Explainable AI (XAI) & Interpretability Lab</span>
          <span className="text-xs font-mono font-normal text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/10">
            TreeSHAP & Partial Dependence
          </span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Complete transparent attribution decomposing model predictions into additive feature contributions.
        </p>
      </div>

      {/* Natural Language Synthesis Banner */}
      <div className="card-surface p-6 border-l-4 border-l-purple-500 bg-gradient-to-r from-purple-950/20 via-[#111827] to-[#111827] space-y-3">
        <div className="flex items-center space-x-2 text-purple-400">
          <Sparkles className="w-5 h-5" />
          <h3 className="text-sm font-bold uppercase tracking-wider">
            Natural Language Decision Synthesis
          </h3>
        </div>
        <p className="text-sm text-slate-200 leading-relaxed">
          {explain.natural_language_summary}
        </p>
        <div className="flex items-center space-x-2 text-xs font-mono text-slate-400 pt-2 border-t border-white/5">
          <span>Target Symbol: <strong className="text-white">{symbol}</strong></span>
          <span>•</span>
          <span>Explainer Method: <strong className="text-purple-400">{explain.explainer_type}</strong></span>
          <span>•</span>
          <span>Sample Size: <strong className="text-white">{explain.background_sample_size}</strong></span>
        </div>
      </div>

      {/* Global Importance vs Local SHAP Waterfall */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Global Feature Importance */}
        <div className="w-full bg-[#111827] rounded-xl p-4 border border-white/5">
          <div className="flex items-center justify-between mb-2 px-2">
            <div>
              <h3 className="text-sm font-semibold text-slate-200">
                Global Feature Importance
              </h3>
              <p className="text-xs text-slate-400">
                Overall relative predictive power across the entire dataset
              </p>
            </div>
          </div>
          <Plot
            data={[
              {
                type: 'bar',
                orientation: 'h',
                y: topGlobalLabels.slice(0, 8).reverse(),
                x: topGlobalWeights.slice(0, 8).reverse(),
                marker: { color: '#3B82F6' },
                text: topGlobalWeights.slice(0, 8).reverse().map((w) => `${(w * 100).toFixed(1)}%`),
                textposition: 'auto',
                textfont: { color: '#FFFFFF', size: 10 },
              },
            ]}
            layout={{
              autosize: true,
              height: 320,
              margin: { l: 140, r: 30, t: 10, b: 30 },
              paper_bgcolor: 'transparent',
              plot_bgcolor: 'transparent',
              showlegend: false,
              xaxis: {
                title: 'Relative Importance Weight',
                titlefont: { color: '#9CA3AF', size: 10 },
                gridcolor: 'rgba(255,255,255,0.06)',
                tickfont: { color: '#9CA3AF', size: 10 },
              },
              yaxis: {
                tickfont: { color: '#E2E8F0', size: 10 },
              },
            }}
            config={{ responsive: true, displayModeBar: false }}
            style={{ width: '100%' }}
          />
        </div>

        {/* Local SHAP Waterfall */}
        <ShapWaterfallChart
          waterfall={explain.shap_waterfall}
          baseValue={explain.shap_base_value}
        />
      </div>

      {/* Partial Dependence Curves */}
      {explain.partial_dependence && explain.partial_dependence.length > 0 && (
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Partial Dependence Profiles (PDP)</h3>
            <p className="text-xs text-slate-400">
              Examining the marginal causal effect of individual indicators on predicted probability
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {explain.partial_dependence.map((pdp, idx) => (
              <PartialDependenceChart
                key={idx}
                featureName={pdp.feature}
                points={pdp.pdp_points}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
