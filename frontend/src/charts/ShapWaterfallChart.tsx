import React from 'react';
import Plot from 'react-plotly.js';
import { ShapWaterfallItem } from '../types';

interface ShapWaterfallChartProps {
  waterfall: ShapWaterfallItem[];
  baseValue: number;
}

export const ShapWaterfallChart: React.FC<ShapWaterfallChartProps> = ({
  waterfall,
  baseValue,
}) => {
  // Take top 8 contributors
  const topItems = waterfall.slice(0, 8).reverse();
  const featureLabels = topItems.map((item) => `${item.feature} (${item.feature_value})`);
  const shapVals = topItems.map((item) => item.shap_value);
  const colors = topItems.map((item) =>
    item.shap_value >= 0 ? '#10B981' : '#EF4444'
  );

  return (
    <div className="w-full bg-[#111827] rounded-xl p-4 border border-white/5">
      <div className="flex items-center justify-between mb-2 px-2">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">
            Local SHAP Feature Contributions
          </h3>
          <p className="text-xs text-slate-400">
            Shapley values showing positive (upward) vs negative (downward) prediction attribution
          </p>
        </div>
        <span className="text-xs font-mono text-slate-400">
          Base value E[f(x)] = {(baseValue * 100).toFixed(1)}%
        </span>
      </div>
      <Plot
        data={[
          {
            type: 'bar',
            orientation: 'h',
            y: featureLabels,
            x: shapVals,
            marker: { color: colors },
            text: shapVals.map((v) => (v > 0 ? `+${v.toFixed(3)}` : v.toFixed(3))),
            textposition: 'auto',
            textfont: { color: '#FFFFFF', size: 10 },
          },
        ]}
        layout={{
          autosize: true,
          height: 320,
          margin: { l: 160, r: 30, t: 10, b: 30 },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          showlegend: false,
          xaxis: {
            title: 'SHAP Value (Marginal Probability Shift)',
            titlefont: { color: '#9CA3AF', size: 10 },
            gridcolor: 'rgba(255,255,255,0.06)',
            tickfont: { color: '#9CA3AF', size: 10 },
            zerolinecolor: 'rgba(255,255,255,0.2)',
          },
          yaxis: {
            tickfont: { color: '#E2E8F0', size: 10 },
          },
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
};
