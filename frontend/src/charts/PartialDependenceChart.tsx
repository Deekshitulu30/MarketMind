import React from 'react';
import Plot from 'react-plotly.js';

interface PartialDependenceProps {
  featureName: string;
  points: Array<{ feature_value: number; predicted_probability: number }>;
}

export const PartialDependenceChart: React.FC<PartialDependenceProps> = ({
  featureName,
  points,
}) => {
  const xVals = points.map((p) => p.feature_value);
  const yVals = points.map((p) => p.predicted_probability * 100);

  return (
    <div className="w-full bg-[#111827] rounded-xl p-4 border border-white/5">
      <div className="mb-2 px-2">
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
          Partial Dependence: {featureName}
        </h4>
        <p className="text-xs text-slate-400">
          Marginal probability of UP direction across feature variation
        </p>
      </div>
      <Plot
        data={[
          {
            type: 'scatter',
            mode: 'lines+markers',
            x: xVals,
            y: yVals,
            line: { color: '#8B5CF6', width: 2.5 },
            marker: { color: '#C4B5FD', size: 5 },
          },
        ]}
        layout={{
          autosize: true,
          height: 220,
          margin: { l: 45, r: 20, t: 10, b: 35 },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          showlegend: false,
          xaxis: {
            title: featureName,
            titlefont: { color: '#9CA3AF', size: 10 },
            gridcolor: 'rgba(255,255,255,0.06)',
            tickfont: { color: '#9CA3AF', size: 9 },
          },
          yaxis: {
            title: 'Prob UP (%)',
            titlefont: { color: '#9CA3AF', size: 10 },
            gridcolor: 'rgba(255,255,255,0.06)',
            tickfont: { color: '#9CA3AF', size: 9 },
          },
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
};
