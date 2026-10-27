import numpy as np
import pandas as pd
from typing import Dict, Any

class RiskEngine:
    @staticmethod
    def calculate_risk_profile(prices: pd.Series) -> Dict[str, Any]:
        """
        Calculates volatility metrics, max drawdown, and educational risk classification.
        """
        clean_p = prices.dropna()
        if len(clean_p) < 5:
            return {"risk_level": "UNKNOWN", "volatility": 0.0, "max_drawdown": 0.0}

        returns = clean_p.pct_change().dropna()
        daily_vol = float(np.std(returns, ddof=1))
        annualized_vol = float(daily_vol * np.sqrt(252))

        # Max Drawdown calculation
        cum_max = clean_p.cummax()
        drawdown = (clean_p - cum_max) / cum_max
        max_drawdown = float(abs(drawdown.min()))

        # Downside Deviation (Semi-deviation for negative returns only)
        neg_returns = returns[returns < 0]
        downside_std = float(np.std(neg_returns, ddof=1)) if len(neg_returns) > 1 else daily_vol
        annualized_downside = float(downside_std * np.sqrt(252))

        # Risk Classification
        if annualized_vol < 0.20 and max_drawdown < 0.15:
            risk_level = "LOW"
            description = "Conservative asset behavior with moderate price swings and controlled drawdowns."
        elif annualized_vol < 0.35 and max_drawdown < 0.30:
            risk_level = "MEDIUM"
            description = "Typical equity market risk with moderate volatility and intermediate cyclical drawdowns."
        else:
            risk_level = "HIGH"
            description = "High volatility profile with substantial potential swings in market valuation."

        return {
            "risk_level": risk_level,
            "description": description,
            "daily_volatility": round(daily_vol, 6),
            "annualized_volatility": round(annualized_vol, 4),
            "annualized_downside_volatility": round(annualized_downside, 4),
            "max_drawdown_pct": round(max_drawdown * 100, 2),
            "var_95_daily_pct": round(float(-np.percentile(returns, 5)) * 100, 2),
            "var_99_daily_pct": round(float(-np.percentile(returns, 1)) * 100, 2),
            "disclaimer": "Educational risk assessment based on historical statistical dispersion. Not an investment rating."
        }
