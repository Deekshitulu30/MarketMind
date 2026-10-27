import React, { useEffect, useRef, useState } from 'react';
import { ExternalLink, RefreshCw, BarChart2, ShieldAlert } from 'lucide-react';

interface TradingViewChartProps {
  symbol: string;
  exchange?: string;
  height?: number | string;
}

declare global {
  interface Window {
    TradingView?: any;
  }
}

export function resolveTradingViewSymbol(symbol: string, exchange?: string): string {
  const cleanSym = symbol.trim().toUpperCase().replace('.NS', '');

  if (cleanSym.includes(':')) {
    return cleanSym;
  }

  if (exchange) {
    const ex = exchange.toUpperCase();
    if (ex === 'NSE' || ex === 'BSE') {
      return `NSE:${cleanSym}`;
    }
    if (ex === 'NYSE') {
      return `NYSE:${cleanSym}`;
    }
    if (ex === 'NASDAQ') {
      return `NASDAQ:${cleanSym}`;
    }
  }

  // Known US tickers
  const usNasdaq = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'GOOG', 'AMZN', 'META', 'TSLA', 'QQQ', 'AMD', 'INTC', 'NFLX', 'ADBE', 'PYPL', 'COST', 'PEP', 'CSCO', 'AVGO', 'TXN', 'QCOM'];
  const usNyse = ['SPY', 'BRK.B', 'BRK-B', 'JPM', 'V', 'WMT', 'MA', 'PG', 'JNJ', 'UNH', 'HD', 'DIS', 'CRM', 'KO', 'XOM', 'CVX', 'NKE', 'LLY', 'ORCL', 'BAC', 'ACN', 'MRK', 'TMO', 'ABT'];

  if (usNasdaq.includes(cleanSym)) {
    return `NASDAQ:${cleanSym}`;
  }
  if (usNyse.includes(cleanSym)) {
    return `NYSE:${cleanSym}`;
  }

  // Default to NSE for Indian symbol universe or NASDAQ for 1-4 character strings
  if (cleanSym.length <= 4 && !['TCS', 'ITC', 'LT', 'SBI', 'NTPC', 'ONGC', 'IOC', 'BEL', 'HAL', 'DLF', 'GAIL', 'VBL', 'SRF', 'UPL', 'BHEL', 'PFC', 'REC', 'RVNL'].includes(cleanSym)) {
    return `NASDAQ:${cleanSym}`;
  }

  return `NSE:${cleanSym}`;
}

export const TradingViewChart: React.FC<TradingViewChartProps> = ({
  symbol,
  exchange,
  height = 560,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const containerId = useRef(`tradingview_${Math.random().toString(36).substring(2, 9)}`);
  const [loadError, setLoadError] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const tvSymbol = resolveTradingViewSymbol(symbol, exchange);

  useEffect(() => {
    let isMounted = true;
    setIsLoading(true);
    setLoadError(false);

    const initWidget = () => {
      if (!isMounted || !containerRef.current) return;

      try {
        // Clear previous content
        containerRef.current.innerHTML = `<div id="${containerId.current}" style="height: 100%; width: 100%;"></div>`;

        if (window.TradingView && typeof window.TradingView.widget === 'function') {
          new window.TradingView.widget({
            autosize: true,
            symbol: tvSymbol,
            interval: 'D',
            timezone: 'Asia/Kolkata',
            theme: 'dark',
            style: '1',
            locale: 'en',
            toolbar_bg: '#0B0F17',
            enable_publishing: false,
            allow_symbol_change: false,
            container_id: containerId.current,
            hide_side_toolbar: false,
            withdateranges: true,
            overrides: {
              'mainSeriesProperties.style': 1,
              'paneProperties.background': '#0B0F17',
              'paneProperties.vertGridProperties.color': 'rgba(255, 255, 255, 0.04)',
              'paneProperties.horzGridProperties.color': 'rgba(255, 255, 255, 0.04)',
              'scalesProperties.textColor': '#94a3b8',
            },
          });
          setIsLoading(false);
        } else {
          throw new Error('TradingView script not ready');
        }
      } catch (err) {
        console.warn('TradingView initialization attempt failed:', err);
        if (isMounted) {
          setIsLoading(false);
          setLoadError(true);
        }
      }
    };

    // Load tv.js script if not present
    if (!window.TradingView) {
      const scriptId = 'tradingview-widget-script';
      let existingScript = document.getElementById(scriptId) as HTMLScriptElement;

      if (!existingScript) {
        const script = document.createElement('script');
        script.id = scriptId;
        script.src = 'https://s3.tradingview.com/tv.js';
        script.async = true;
        script.onload = () => {
          if (isMounted) initWidget();
        };
        script.onerror = () => {
          if (isMounted) {
            setIsLoading(false);
            setLoadError(true);
          }
        };
        document.head.appendChild(script);
      } else {
        existingScript.addEventListener('load', initWidget);
      }
    } else {
      initWidget();
    }

    return () => {
      isMounted = false;
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [tvSymbol]);

  return (
    <div className="card-surface p-4 rounded-2xl border border-white/10 overflow-hidden relative shadow-2xl flex flex-col">
      {/* Header bar */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-white/5 px-2">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <BarChart2 className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-white tracking-tight">{symbol}</span>
              <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                {tvSymbol}
              </span>
              <span className="text-[10px] text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/5">
                Official TradingView Advanced Embed
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Live candlesticks, drawing tools, indicators, and multi-timeframe OHLCV.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <a
            href={`https://www.tradingview.com/symbols/${tvSymbol.replace(':', '-')}/`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1 text-xs text-slate-400 hover:text-blue-400 transition-colors bg-white/5 hover:bg-white/10 px-2.5 py-1 rounded-lg border border-white/5"
          >
            <span>TradingView</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>

      {/* Chart Canvas */}
      <div
        className="w-full rounded-xl overflow-hidden bg-[#0B0F17] relative border border-white/5"
        style={{ height: typeof height === 'number' ? `${height}px` : height, minHeight: '480px' }}
      >
        {isLoading && (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-[#0B0F17]/90 backdrop-blur-sm text-slate-400 space-y-3">
            <RefreshCw className="w-6 h-6 animate-spin text-blue-400" />
            <span className="text-xs font-mono">Initializing TradingView Advanced Chart for {tvSymbol}...</span>
          </div>
        )}

        {loadError && (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center bg-[#0B0F17] text-slate-400 p-6 text-center space-y-3">
            <ShieldAlert className="w-8 h-8 text-amber-400" />
            <h4 className="text-sm font-semibold text-white">TradingView Widget Offline or Restricted</h4>
            <p className="text-xs text-slate-400 max-w-md">
              Unable to load external TradingView CDN script. Please verify your internet connection or ad-blocker settings.
            </p>
          </div>
        )}

        <div ref={containerRef} className="w-full h-full" />
      </div>

      {/* Footer attribution */}
      <div className="mt-2 pt-2 flex items-center justify-between text-[11px] text-slate-500 font-mono border-t border-white/5 px-1">
        <span>Charting provided by TradingView free embed widget</span>
        <span>Independent container sandbox</span>
      </div>
    </div>
  );
};
