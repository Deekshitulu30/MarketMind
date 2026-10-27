import React from 'react';
import Plot from 'react-plotly.js';

interface BivariateScatterProps {
  title: string;
  xLabel: string;
  yLabel: string;
  slope: number;
  intercept: number;
  rSquared: number;
  pValue: number;
  scatterPoints: Array<{ x: number; y: number }>;
  regressionLine: Array<{ x: number; y: number }>;
}

export const BivariateScatterChart: React.FC<BivariateScatterProps> = ({
  title,
  xLabel,
  yLabel,
  slope,
  intercept,
  rSquared,
  pValue,
  scatterPoints,
  regressionLine,
}) => {
  const xVals = scatterPoints.map((p) => p.x);
  const yVals = scatterPoints.map((p) => p.y);

  const lineX = regressionLine.map((p) => p.x);
  const lineY = regressionLine.map((p) => p.y);

  return (
    <div className="w-full bg-[#111827] rounded-xl p-4 border border-white/5">
      <div className="flex items-center justify-between mb-2 px-2">
        <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
        <div className="flex space-x-3 text-xs font-mono text-slate-400">
          <span>Slope: {slope.toFixed(4)}</span>
          <span className="text-blue-400 font-semibold">R² = {rSquared.toFixed(4)}</span>
          <span>p = {pValue < 0.001 ? '< 0.001' : pValue.toFixed(4)}</span>
        </div>
      </div>
      <Plot
        data={[
          {
            type: 'scatter',
            mode: 'markers',
            x: xVals,
            y: yVals,
            name: 'Data Points',
            marker: { color: '#38BDF8', size: 5, opacity: 0.5 },
          },
          {
            type: 'scatter',
            mode: 'lines',
            x: lineX,
            y: lineY,
            name: 'OLS Fit',
            line: { color: '#F43F5E', width: 2 },
          },
        ]}
        layout={{
          autosize: true,
          height: 280,
          margin: { l: 50, r: 20, t: 10, b: 40 },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          showlegend: false,
          xaxis: {
            title: xLabel,
            titlefont: { color: '#9CA3AF', size: 10 },
            gridcolor: 'rgba(255,255,255,0.06)',
            tickfont: { color: '#9CA3AF', size: 10 },
          },
          yaxis: {
            title: yLabel,
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
