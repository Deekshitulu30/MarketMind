import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.data.repository import StockRepository
from app.statistics.descriptive import compute_descriptive_stats
from app.statistics.distributions import compute_return_series, analyze_return_distribution
from app.statistics.correlation import compute_correlation_matrix, compute_scatter_regression
from app.statistics.hypothesis import run_hypothesis_test

class StatisticsEngine:
    @staticmethod
    def analyze_stock(
        db: Session,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Executes complete statistical analysis suite for a given stock.
        """
        stock = StockRepository.get_by_symbol(db, symbol)
        df = StockRepository.get_price_history_df(db, symbol, start_date, end_date)

        # Returns
        ret_dict = compute_return_series(df["close"])
        df["daily_return"] = ret_dict["pct_returns"]
        df["log_return"] = ret_dict["log_returns"]

        # Descriptive Statistics
        price_stats = compute_descriptive_stats(df["close"])
        return_stats = compute_descriptive_stats(df["daily_return"])
        volume_stats = compute_descriptive_stats(df["volume"])

        # Return Distribution & VaR
        distribution_analysis = analyze_return_distribution(df["daily_return"])

        # Volatility (20-day rolling annualized)
        rolling_vol = (df["daily_return"].rolling(window=20).std() * (252**0.5)).dropna()
        volatility_stats = compute_descriptive_stats(rolling_vol)

        # Bivariate relationships & Correlation
        # 1. Volume vs Daily Return
        vol_vs_ret = compute_scatter_regression(
            x_series=df["volume"] / 1_000_000,  # in Millions
            y_series=df["daily_return"] * 100,  # in %
            x_label="Volume (M)",
            y_label="Daily Return (%)"
        )

        # 2. Lagged Return vs Current Return (autocorrelation)
        lag1_ret = df["daily_return"].shift(1)
        lag_vs_ret = compute_scatter_regression(
            x_series=lag1_ret * 100,
            y_series=df["daily_return"] * 100,
            x_label="Lag 1 Return (%)",
            y_label="Current Return (%)"
        )

        # Correlation Matrix across core variables
        corr_input_df = pd.DataFrame({
            "Price": df["close"],
            "Daily Return": df["daily_return"],
            "Volume": df["volume"],
            "Volatility (20d)": df["daily_return"].rolling(20).std()
        })
        corr_matrix = compute_correlation_matrix(corr_input_df)

        # Hypothesis Testing: High Volume vs Normal Volume returns
        vol_median = df["volume"].median()
        high_vol_returns = df[df["volume"] > vol_median]["daily_return"]
        normal_vol_returns = df[df["volume"] <= vol_median]["daily_return"]
        hyp_test = run_hypothesis_test(
            sample_a=high_vol_returns,
            sample_b=normal_vol_returns,
            label_a="High-Volume Days (> Median)",
            label_b="Normal-Volume Days (<= Median)",
            alpha=0.05
        )

        def _fmt_date(d):
            return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)[:10]

        # Time series points for line charts (downsampled if long)
        ts_points = [
            {
                "date": _fmt_date(row["date"]),
                "open": round(float(row["open"]), 2),
                "high": round(float(row["high"]), 2),
                "low": round(float(row["low"]), 2),
                "close": round(float(row["close"]), 2),
                "volume": int(row["volume"]),
                "daily_return": round(float(row["daily_return"]), 4) if pd.notnull(row["daily_return"]) else 0.0
            }
            for _, row in df.iterrows()
        ]

        correlation_payload = {
            "columns": corr_matrix.get("columns", []),
            "pearson_matrix": corr_matrix.get("pearson_matrix", []),
            "spearman_matrix": corr_matrix.get("spearman_matrix", []),
            "bivariate_regressions": {
                "volume_vs_return": vol_vs_ret,
                "lag1_vs_return": lag_vs_ret,
                "return_vs_market": vol_vs_ret
            }
        }

        return {
            "symbol": stock.symbol,
            "company_name": stock.company_name,
            "period": {
                "start": _fmt_date(df["date"].min()),
                "end": _fmt_date(df["date"].max()),
                "total_trading_days": len(df)
            },
            "price_summary": price_stats,
            "return_summary": return_stats,
            "volume_summary": volume_stats,
            "volatility_summary": volatility_stats,
            "distribution_analysis": distribution_analysis,
            "bivariate_regressions": {
                "volume_vs_return": vol_vs_ret,
                "lag1_vs_return": lag_vs_ret,
                "return_vs_market": vol_vs_ret
            },
            "correlation_matrix": corr_matrix,
            "hypothesis_test": hyp_test,
            "time_series": ts_points,

            # Aliases matching frontend StatisticsLab.tsx
            "descriptive": return_stats,
            "distribution": distribution_analysis,
            "correlation": correlation_payload
        }
