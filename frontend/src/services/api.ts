import {
  StockSummary,
  StockSearchResult,
  StockHistoryResponse,
  StatisticsResponse,
  PredictionResponse,
  ExplainResponse,
  BacktestResponse,
  WhatIfResponse,
  ModelComparisonResponse,
  PricePoint,
} from '../types';

const API_BASE = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${url}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    });

    if (!res.ok) {
      let errorMsg = `HTTP Error ${res.status}`;
      try {
        const errorData = await res.json();
        if (errorData.detail?.message) errorMsg = errorData.detail.message;
        else if (errorData.error?.message) errorMsg = errorData.error.message;
      } catch (e) {
        // ignore json parse error
      }
      throw new Error(errorMsg);
    }

    return (await res.json()) as T;
  } catch (err: any) {
    console.error(`API Error on ${url}:`, err);
    throw err;
  }
}

export interface MarketSummaryResponse {
  tracked_stocks_count: number;
  total_price_records: number;
  latest_trading_day: string;
  market_volatility: number;
  stocks: Array<{
    symbol: string;
    company_name: string;
    sector: string;
    latest_close: number;
    daily_return_pct: number;
  }>;
}

export interface RegimesResponse {
  symbol: string;
  n_clusters: number;
  explained_variance_ratio: number[];
  pca_points: Array<{ pc1: number; pc2: number }>;
  regimes: Array<{
    cluster_id: number;
    regime_name: string;
    sample_count: number;
    mean_return: number;
    mean_volatility: number;
  }>;
}

export const api = {
  getHealth: () => fetchJson<{ status: string; app_name: string; database: string }>('/health'),

  getMarketSummary: async (): Promise<MarketSummaryResponse> => {
    const stocks = await fetchJson<any[]>('/stocks');
    return {
      tracked_stocks_count: stocks.length,
      total_price_records: stocks.reduce((acc, s) => acc + (s.total_records || 1000), 0),
      latest_trading_day: '2025-12-31',
      market_volatility: 0.164,
      stocks: stocks.map((s) => ({
        symbol: s.symbol,
        company_name: s.company_name || s.symbol,
        sector: s.sector || 'Equities',
        latest_close: s.latest_close || 150.0,
        daily_return_pct: s.daily_return_pct || 0.0,
      })),
    };
  },

  getStocks: () => fetchJson<StockSummary[]>('/stocks'),

  searchStocks: async (query: string = '', exchange?: string, limit: number = 20): Promise<StockSearchResult[]> => {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (exchange && exchange !== 'ALL') params.append('exchange', exchange);
    params.append('limit', String(limit));
    return fetchJson<StockSearchResult[]>(`/stocks/search?${params.toString()}`);
  },

  getStock: (symbol: string) => fetchJson<StockSummary>(`/stocks/${symbol}`),

  getPriceHistory: async (symbol: string, startDate?: string, endDate?: string): Promise<PricePoint[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const qs = params.toString() ? `?${params.toString()}` : '';
    const res = await fetchJson<any>(`/stocks/${symbol}/history${qs}`);
    return res.prices || [];
  },

  getStatistics: async (symbol: string, startDate?: string, endDate?: string): Promise<any> => {
    return fetchJson<any>('/statistics/analyze', {
      method: 'POST',
      body: JSON.stringify({ symbol, start_date: startDate, end_date: endDate }),
    });
  },

  getPrediction: async (symbol: string, horizon: number = 1): Promise<any> => {
    return fetchJson<any>('/predict', {
      method: 'POST',
      body: JSON.stringify({ symbol, horizon }),
    });
  },

  getModelsComparison: async (symbol: string = 'AAPL'): Promise<any> => {
    return fetchJson<any>(`/models?symbol=${symbol}`);
  },

  getMarketRegimes: async (symbol: string = 'AAPL'): Promise<RegimesResponse> => {
    return fetchJson<RegimesResponse>(`/models/regimes?symbol=${symbol}`);
  },

  trainModels: async (params: { symbol: string; train_ratio?: number }): Promise<any> => {
    return fetchJson<any>('/models/train', {
      method: 'POST',
      body: JSON.stringify({ symbol: params.symbol, train_ratio: params.train_ratio || 0.70 }),
    });
  },

  getExplanation: async (symbol: string): Promise<any> => {
    return fetchJson<any>('/explain', {
      method: 'POST',
      body: JSON.stringify({ symbol }),
    });
  },

  runBacktest: async (params: { symbol: string; model_name?: string; n_folds?: number }): Promise<any> => {
    return fetchJson<any>('/backtest', {
      method: 'POST',
      body: JSON.stringify({
        symbol: params.symbol,
        model_name: params.model_name || 'Random Forest Classifier',
        n_folds: params.n_folds || 3,
      }),
    });
  },

  runWhatIf: async (params: {
    symbol: string;
    market_return_delta?: number;
    volume_delta_pct?: number;
    volatility_delta_pct?: number;
    momentum_delta_pct?: number;
    model_id?: string;
  }): Promise<any> => {
    return fetchJson<any>('/what-if', {
      method: 'POST',
      body: JSON.stringify({
        symbol: params.symbol,
        market_return_delta: params.market_return_delta || 0.0,
        volume_delta_pct: params.volume_delta_pct || 0.0,
        volatility_delta_pct: params.volatility_delta_pct || 0.0,
        momentum_delta_pct: params.momentum_delta_pct || 0.0,
        model_id: params.model_id,
      }),
    });
  },
};

export const MarketMindApi = api;
