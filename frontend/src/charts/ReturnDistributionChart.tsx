import React from 'react';
import Plot from 'react-plotly.js';
import { DistributionAnalysis } from '../types';

interface ReturnDistributionChartProps {
  distribution: DistributionAnalysis;
  symbol: string;
}

export const ReturnDistributionChart: React.FC<ReturnDistributionChartProps> = ({
  distribution,
  symbol,
}) => {
  const bins = distribution.histogram_bins || [];
  const binCenters = bins.map((b) => b.bin_center * 100);
  const densities = bins.map((b) => b.density / 100);

  const normalCurve = distribution.fitted_normal_curve || [];
  const normX = normalCurve.map((p) => p.x * 100);
  const normY = normalCurve.map((p) => p.y / 100);

  return (
    <div className="w-full bg-[#111827] rounded-xl p-4 border border-white/5">
      <div className="flex items-center justify-between mb-3 px-2">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">
            Daily Return Distribution & Normal Fit
          </h3>
          <p className="text-xs text-slate-400">
            Empirical histogram vs theoretical Gaussian bell curve
          </p>
        </div>
        <div className="flex space-x-3 text-xs font-mono">
          <span className="text-emerald-400">
            P(R &gt; 0): {distribution.prob_positive_pct}%
          </span>
          <span className="text-rose-400">
            P(R &lt; 0): {distribution.prob_negative_pct}%
          </span>
        </div>
      </div>
      <Plot
        data={[
          {
            type: 'bar',
            x: binCenters,
            y: densities,
            name: 'Empirical Distribution',
            marker: { color: '#3B82F6', opacity: 0.6 },
          },
          {
            type: 'scatter',
            mode: 'lines',
            x: normX,
            y: normY,
            name: 'Fitted Normal Curve',
            line: { color: '#F59E0B', width: 2.5 },
          },
        ]}
        layout={{
          autosize: true,
          height: 350,
          margin: { l: 50, r: 20, t: 10, b: 40 },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          legend: {
            orientation: 'h',
            y: 1.12,
            font: { color: '#9CA3AF', size: 11 },
          },
          xaxis: {
            title: 'Daily Return (%)',
            titlefont: { color: '#9CA3AF', size: 11 },
            gridcolor: 'rgba(255,255,255,0.06)',
            tickfont: { color: '#9CA3AF', size: 10 },
          },
          yaxis: {
            title: 'Density',
            titlefont: { color: '#9CA3AF', size: 11 },
            gridcolor: 'rgba(255,255,255,0.06)',
            tickfont: { color: '#9CA3AF', size: 10 },
          },
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
};
