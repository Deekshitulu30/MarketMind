import React, { useState } from 'react';
import Plot from 'react-plotly.js';

interface CorrelationHeatmapProps {
  columns: string[];
  pearsonMatrix: number[][];
  spearmanMatrix: number[][];
}

export const CorrelationHeatmap: React.FC<CorrelationHeatmapProps> = ({
  columns,
  pearsonMatrix,
  spearmanMatrix,
}) => {
  const [method, setMethod] = useState<'pearson' | 'spearman'>('pearson');
  const activeMatrix = method === 'pearson' ? pearsonMatrix : spearmanMatrix;

  return (
    <div className="w-full bg-[#111827] rounded-xl p-4 border border-white/5">
      <div className="flex items-center justify-between mb-3 px-2">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">
            Variable Correlation Heatmap
          </h3>
          <p className="text-xs text-slate-400">
            Linear (Pearson) and Monotonic (Spearman) relationship strengths
          </p>
        </div>
        <div className="flex bg-[#0B0F17] rounded-lg p-0.5 border border-white/10 text-xs">
          <button
            onClick={() => setMethod('pearson')}
            className={`px-3 py-1 rounded-md transition-colors ${
              method === 'pearson'
                ? 'bg-blue-600 text-white font-medium'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Pearson
          </button>
          <button
            onClick={() => setMethod('spearman')}
            className={`px-3 py-1 rounded-md transition-colors ${
              method === 'spearman'
                ? 'bg-blue-600 text-white font-medium'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Spearman
          </button>
        </div>
      </div>
      <Plot
        data={[
          {
            type: 'heatmap',
            z: activeMatrix,
            x: columns,
            y: columns,
            colorscale: [
              [0, '#EF4444'],
              [0.5, '#1E293B'],
              [1, '#10B981'],
            ],
            zmin: -1,
            zmax: 1,
            text: activeMatrix.map((row) => row.map((v) => v.toFixed(2))) as any,
            texttemplate: '%{text}',
            textfont: { color: '#F3F4F6', size: 11 },
          } as any,
        ]}
        layout={{
          autosize: true,
          height: 350,
          margin: { l: 80, r: 20, t: 20, b: 60 },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          xaxis: {
            tickfont: { color: '#9CA3AF', size: 10 },
          },
          yaxis: {
            tickfont: { color: '#9CA3AF', size: 10 },
            autorange: 'reversed',
          },
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
};
