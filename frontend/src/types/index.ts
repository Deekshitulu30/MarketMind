export interface StockSummary {
  id: string;
  symbol: string;
  company_name: string;
  exchange: string;
  currency: string;
  sector?: string;
}

export interface StockSearchResult {
  symbol: string;
  company_name: string;
  exchange: string;
  currency: string;
  sector?: string;
  isin?: string;
  tradingview_symbol: string;
  yfinance_ticker: string;
}

export interface PricePoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  adjusted_close: number;
  volume: number;
}

export interface StockHistoryResponse {
  symbol: string;
  company_name: string;
  total_records: number;
  start_date: string;
  end_date: string;
  prices: PricePoint[];
}

export interface DescriptiveStats {
  count: number;
  mean: number;
  median: number;
  mode: number;
  variance: number;
  std_dev: number;
  min: number;
  max: number;
  range: number;
  q25: number;
  q75: number;
  iqr: number;
  skewness: number;
  kurtosis: number;
  outliers_count: number;
  outliers_pct: number;
}

export interface HistogramBin {
  bin_start: number;
  bin_end: number;
  bin_center: number;
  density: number;
  count: number;
}

export interface DistributionAnalysis {
  mean_daily_return: number;
  std_daily_return: number;
  annualized_return: number;
  annualized_volatility: number;
  sharpe_ratio: number;
  prob_positive_pct: number;
  prob_negative_pct: number;
  prob_zero_pct: number;
  var_95_historical: number;
  var_99_historical: number;
  var_95_parametric: number;
  var_99_parametric: number;
  histogram_bins: HistogramBin[];
  fitted_normal_curve: Array<{ x: number; y: number }>;
}

export interface HypothesisTestResult {
  test_name: string;
  null_hypothesis: string;
  alternative_hypothesis: string;
  significance_level: number;
  sample_a_label: string;
  sample_a_size: number;
  sample_a_mean: number;
  sample_a_std: number;
  sample_b_label: string;
  sample_b_size: number;
  sample_b_mean: number;
  sample_b_std: number;
  t_statistic: number;
  p_value: number;
  reject_null: boolean;
  decision: string;
  interpretation: string;
}

export interface StatisticsResponse {
  symbol: string;
  company_name: string;
  period: {
    start: string;
    end: string;
    total_trading_days: number;
  };
  price_summary: DescriptiveStats;
  return_summary: DescriptiveStats;
  volume_summary: DescriptiveStats;
  volatility_summary: DescriptiveStats;
  distribution_analysis: DistributionAnalysis;
  bivariate_regressions: {
    volume_vs_return: {
      x_label: string;
      y_label: string;
      slope: number;
      intercept: number;
      r_squared: number;
      p_value: number;
      scatter_points: Array<{ x: number; y: number }>;
      regression_line: Array<{ x: number; y: number }>;
    };
    lag1_vs_return: {
      x_label: string;
      y_label: string;
      slope: number;
      intercept: number;
      r_squared: number;
      p_value: number;
      scatter_points: Array<{ x: number; y: number }>;
      regression_line: Array<{ x: number; y: number }>;
    };
  };
  correlation_matrix: {
    columns: string[];
    pearson_matrix: number[][];
    spearman_matrix: number[][];
  };
  hypothesis_test: HypothesisTestResult;
  time_series: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    daily_return: number;
  }>;
}

export interface RiskProfile {
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  description: string;
  daily_volatility: number;
  annualized_volatility: number;
  annualized_downside_volatility: number;
  max_drawdown_pct: number;
  var_95_daily_pct: number;
  var_99_daily_pct: number;
  disclaimer: string;
}

export interface ModelReferenceLevel {
  label: string;
  value: number;
  buffer: number;
  formula: string;
}

export interface ModelReferenceLevelsPayload {
  is_educational_reference: boolean;
  model_version: string;
  confidence_pct: number;
  direction: 'UP' | 'DOWN';
  last_close: number;
  expected_return_pct: number;
  predicted_price: number;
  atr_14: number;
  multipliers: {
    target_k: number;
    stop_loss_m: number;
  };
  reference_target: ModelReferenceLevel;
  reference_stop_loss: ModelReferenceLevel;
  risk_reward_ratio: number;
  mandatory_disclaimer: string;
  methodology: {
    technique: string;
    atr_period: number;
    formula_description: string;
    purpose: string;
  };
}

export interface PredictionResponse {
  prediction_id: string;
  symbol: string;
  company_name: string;
  current_price: number;
  data_cutoff: string;
  prediction_generated_at: string;
  horizon_days: number;
  predicted_direction: 'UP' | 'DOWN';
  probability_up_pct: number;
  confidence_pct: number;
  expected_return_pct: number;
  predicted_price: number;
  risk_profile: RiskProfile;
  reference_levels?: ModelReferenceLevelsPayload;
  model_metadata: {
    model_id: string;
    model_name: string;
    model_version: string;
    validation_accuracy: number;
  };
  disclaimer: string;
}

export interface ShapWaterfallItem {
  feature: string;
  feature_value: number;
  shap_value: number;
  impact: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  abs_impact: number;
}

export interface GlobalImportanceItem {
  feature: string;
  importance: number;
  percentage: number;
}

export interface ExplainResponse {
  symbol: string;
  company_name: string;
  model_metadata: {
    model_id: string;
    model_name: string;
    model_version: string;
  };
  data_cutoff: string;
  global_feature_importance: GlobalImportanceItem[];
  shap_waterfall: ShapWaterfallItem[];
  base_value: number;
  partial_dependence: Record<string, Array<{ feature_value: number; predicted_probability: number }>>;
  natural_language_summary: string;
}

export interface FoldResult {
  fold_id: number;
  train_period: string;
  test_period: string;
  train_samples: number;
  test_samples: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  confusion_matrix: number[][];
  strategy_return_pct: number;
  benchmark_return_pct: number;
}

export interface BacktestResponse {
  backtest_id?: string;
  symbol: string;
  company_name: string;
  model_name: string;
  strategy: string;
  total_folds: number;
  summary_metrics: {
    mean_accuracy: number;
    mean_f1_score: number;
    min_accuracy: number;
    max_accuracy: number;
  };
  fold_results: FoldResult[];
  time_series_evaluation: Array<{
    date: string;
    actual_direction: string;
    predicted_direction: string;
    probability_up: number;
    actual_return_pct: number;
    strategy_cumulative_return_pct: number;
    benchmark_cumulative_return_pct: number;
    is_correct: boolean;
  }>;
}

export interface WhatIfResponse {
  symbol: string;
  company_name: string;
  data_cutoff: string;
  model_metadata: {
    model_id: string;
    model_name: string;
    model_version: string;
  };
  scenario_inputs: {
    market_return_delta_pct: number;
    volume_delta_pct: number;
    volatility_delta_pct: number;
    momentum_delta_pct: number;
  };
  baseline: {
    predicted_direction: string;
    probability_up_pct: number;
    expected_return_pct: number;
    risk_level: string;
  };
  scenario: {
    predicted_direction: string;
    probability_up_pct: number;
    expected_return_pct: number;
    risk_level: string;
  };
  comparison: {
    probability_up_delta_pct: number;
    expected_return_delta_pct: number;
    direction_shifted: boolean;
  };
  assumptions: string[];
  disclaimer: string;
}

export interface ModelComparisonResponse {
  symbol: string;
  dataset_splits: {
    train_samples: number;
    val_samples: number;
    test_samples: number;
    train_period: string;
    test_period: string;
  };
  classification_models: Array<{
    model_id: string;
    model_name: string;
    version: string;
    metrics: Record<string, any>;
    is_baseline: boolean;
  }>;
  regression_models: Array<{
    model_id: string;
    model_name: string;
    version: string;
    metrics: Record<string, any>;
    is_baseline: boolean;
  }>;
  clustering: {
    inertia: number;
    cluster_counts: Record<string, number>;
    regime_labels: Record<string, string>;
  };
  pca: {
    explained_variance_ratio: number[];
    total_explained_variance: number;
    feature_loadings: Array<{ feature: string; pc1_loading: number; pc2_loading: number }>;
    sample_points: Array<{ pc1: number; pc2: number; pc3?: number }>;
  };
  best_classification_model: {
    model_id: string;
    model_name: string;
    model_version: string;
  };
}
