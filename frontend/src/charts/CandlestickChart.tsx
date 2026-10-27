import React from 'react';
import Plot from 'react-plotly.js';
import { PricePoint } from '../types';

interface CandlestickChartProps {
  prices: PricePoint[];
  symbol: string;
}

export const CandlestickChart: React.FC<CandlestickChartProps> = ({ prices, symbol }) => {
  const dates = prices.map((p) => p.date);
  const opens = prices.map((p) => p.open);
  const highs = prices.map((p) => p.high);
  const lows = prices.map((p) => p.low);
  const closes = prices.map((p) => p.close);
  const volumes = prices.map((p) => p.volume);

  const colors = prices.map((p) => (p.close >= p.open ? '#10B981' : '#EF4444'));

  return (
    <div className="w-full bg-[#111827] rounded-xl p-4 border border-white/5">
      <div className="flex items-center justify-between mb-3 px-2">
        <h3 className="text-sm font-semibold text-slate-200">
          {symbol} Price & Volume History
        </h3>
        <span className="text-xs text-slate-400 font-mono">
          {prices.length} trading days
        </span>
      </div>
      <Plot
        data={[
          {
            type: 'candlestick',
            x: dates,
            open: opens,
            high: highs,
            low: lows,
            close: closes,
            increasing: { line: { color: '#10B981' } },
            decreasing: { line: { color: '#EF4444' } },
            name: `${symbol} Price`,
            yaxis: 'y1',
          },
          {
            type: 'bar',
            x: dates,
            y: volumes,
            marker: { color: colors, opacity: 0.3 },
            name: 'Volume',
            yaxis: 'y2',
          },
        ]}
        layout={{
          autosize: true,
          height: 480,
          margin: { l: 50, r: 40, t: 20, b: 40 },
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          showlegend: false,
          xaxis: {
            rangeslider: { visible: false },
            gridcolor: 'rgba(255,255,255,0.06)',
            tickfont: { color: '#9CA3AF', size: 11 },
          },
          yaxis: {
            title: 'Price ($)',
            titlefont: { color: '#9CA3AF', size: 12 },
            gridcolor: 'rgba(255,255,255,0.06)',
            tickfont: { color: '#9CA3AF', size: 11 },
            domain: [0.3, 1.0],
          },
          yaxis2: {
            title: 'Volume',
            titlefont: { color: '#9CA3AF', size: 10 },
            gridcolor: 'transparent',
            tickfont: { color: '#6B7280', size: 9 },
            domain: [0.0, 0.22],
          },
        }}
        config={{ responsive: true, displayModeBar: false }}
        style={{ width: '100%' }}
      />
    </div>
  );
};
