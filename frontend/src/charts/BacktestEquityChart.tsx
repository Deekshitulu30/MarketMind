import React from 'react';
import Plot from 'react-plotly.js';

interface BacktestEquityChartProps {
  series: Array<{
    date: string;
    strategy_cumulative_return_pct: number;
    benchmark_cumulative_return_pct: number;
  }>;
}

export const BacktestEquityChart: React.FC<BacktestEquityChartProps> = ({ series }) => {
  const dates = series.map((s) => s.date);
  const strategy = series.map((s) => s.strategy_cumulative_return_pct);
  const benchmark = series.map((s) => s.benchmark_cumulative_return_pct);

  return (
    <div className="w-full bg-[#111827] rounded-xl p-4 border border-white/5">
      <div className="flex items-center justify-between mb-3 px-2">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">
            Out-of-Sample Cumulative Strategy Returns
          </h3>
          <p className="text-xs text-slate-400">
            Chronological walk-forward strategy vs Buy & Hold benchmark
          </p>
        </div>
        <div className="flex space-x-4 text-xs font-mono">
          <span className="text-blue-400">
            Strategy: {strategy[strategy.length - 1]?.toFixed(2)}%
          </span>
          <span className="text-slate-400">
            Benchmark: {benchmark[benchmark.length - 1]?.toFixed(2)}%
          </span>
        </div>
      </div>
      <Plot
        data={[
          {
            type: 'scatter',
            mode: 'lines',
            x: dates,
            y: strategy,
            name: 'ML Directional Strategy',
            line: { color: '#3B82F6', width: 2.5 },
          },
          {
            type: 'scatter',
            mode: 'lines',
            x: dates,
            y: benchmark,
            name: 'Buy & Hold Benchmark',
            line: { color: '#9CA3AF', width: 1.5, dash: 'dot' },
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
            gridcolor: 'rgba(255,255,255,0.06)',
            tickfont: { color: '#9CA3AF', size: 10 },
          },
          yaxis: {
            title: 'Cumulative Return (%)',
            titlefont: { color: '#9CA3AF', size: 11 },
            gridcolor: 'rgba(255,255,255,0.06)',
            tickfont: { color: '#9CA3AF', size: 10 },
            zerolinecolor: 'rgba(255,255,255,0.2)',
          },
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
};
