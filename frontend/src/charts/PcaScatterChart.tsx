import React from 'react';
import Plot from 'react-plotly.js';

interface PcaScatterProps {
  points: Array<{ pc1: number; pc2: number }>;
  explainedVarianceRatio: number[];
}

export const PcaScatterChart: React.FC<PcaScatterProps> = ({
  points,
  explainedVarianceRatio,
}) => {
  const pc1 = points.map((p) => p.pc1);
  const pc2 = points.map((p) => p.pc2);

  const pc1Pct = ((explainedVarianceRatio[0] || 0) * 100).toFixed(1);
  const pc2Pct = ((explainedVarianceRatio[1] || 0) * 100).toFixed(1);

  return (
    <div className="w-full bg-[#111827] rounded-xl p-4 border border-white/5">
      <div className="flex items-center justify-between mb-2 px-2">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">
            PCA 2D Feature Space Projection
          </h3>
          <p className="text-xs text-slate-400">
            Dimensionality reduction projecting high-dimensional technical features
          </p>
        </div>
        <span className="text-xs font-mono text-blue-400">
          Total Exp. Var: {(((explainedVarianceRatio[0] || 0) + (explainedVarianceRatio[1] || 0)) * 100).toFixed(1)}%
        </span>
      </div>
      <Plot
        data={[
          {
            type: 'scatter',
            mode: 'markers',
            x: pc1,
            y: pc2,
            marker: {
              color: pc1.map((v, i) => i),
              colorscale: 'Viridis',
              size: 6,
              opacity: 0.7,
            },
            name: 'State Points',
          },
        ]}
        layout={{
          autosize: true,
          height: 300,
          margin: { l: 50, r: 20, t: 10, b: 40 },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          showlegend: false,
          xaxis: {
            title: `PC1 (${pc1Pct}% variance)`,
            titlefont: { color: '#9CA3AF', size: 10 },
            gridcolor: 'rgba(255,255,255,0.06)',
            tickfont: { color: '#9CA3AF', size: 10 },
          },
          yaxis: {
            title: `PC2 (${pc2Pct}% variance)`,
            titlefont: { color: '#9CA3AF', size: 10 },
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
