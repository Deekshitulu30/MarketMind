import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import InvalidDataException, ModelNotFoundException
from app.data.repository import StockRepository
from app.features.pipeline import FeaturePipeline, FEATURE_COLUMNS
from app.models.registry import ModelRegistry
from app.database.models import ScenarioRecord

class WhatIfSimulator:
    @staticmethod
    def simulate_scenario(
        db: Session,
        symbol: str,
        model_id: Optional[str] = None,
        market_return_delta: float = 0.0,   # e.g. +0.02 (+2%)
        volume_delta_pct: float = 0.0,      # e.g. +0.15 (+15%)
        volatility_delta_pct: float = 0.0,  # e.g. -0.10 (-10%)
        momentum_delta_pct: float = 0.0     # e.g. +0.05 (+5%)
    ) -> Dict[str, Any]:
        """
        Simulates hypothetical market scenario changes against a frozen baseline
        and compares directional probability, expected return, and risk sensitivity.
        """
        # Validate Bounds
        if not (-0.15 <= market_return_delta <= 0.15):
            raise InvalidDataException("market_return_delta must be between -15% and +15% (-0.15 to +0.15).")
        if not (-0.80 <= volume_delta_pct <= 0.80):
            raise InvalidDataException("volume_delta_pct must be between -80% and +80% (-0.80 to +0.80).")
        if not (-0.80 <= volatility_delta_pct <= 0.80):
            raise InvalidDataException("volatility_delta_pct must be between -80% and +80% (-0.80 to +0.80).")
        if not (-0.80 <= momentum_delta_pct <= 0.80):
            raise InvalidDataException("momentum_delta_pct must be between -80% and +80% (-0.80 to +0.80).")

        stock = StockRepository.get_by_symbol(db, symbol)
        df_stock = StockRepository.get_price_history_df(db, symbol)

        df_market = None
        try:
            if symbol != "SPY":
                df_market = StockRepository.get_price_history_df(db, "SPY")
        except Exception:
            pass

        features_df = FeaturePipeline.generate_features_df(df_stock, df_market)
        latest_row = features_df.iloc[-1]
        data_cutoff = latest_row["date"]

        # Base Feature Vector
        X_base = pd.DataFrame([latest_row[FEATURE_COLUMNS].to_dict()]).fillna(0.0)

        # Scenario Feature Vector (apply synthetic changes)
        X_scenario = X_base.copy()
        
        if "market_return" in X_scenario.columns:
            X_scenario["market_return"] += market_return_delta

        if "volume_change" in X_scenario.columns:
            X_scenario["volume_change"] = X_scenario["volume_change"] * (1.0 + volume_delta_pct)
        if "volume_ratio_20" in X_scenario.columns:
            X_scenario["volume_ratio_20"] = X_scenario["volume_ratio_20"] * (1.0 + volume_delta_pct)

        if "volatility" in X_scenario.columns:
            X_scenario["volatility"] = (X_scenario["volatility"] * (1.0 + volatility_delta_pct)).clip(lower=0.01)
        if "rolling_std_5" in X_scenario.columns:
            X_scenario["rolling_std_5"] = (X_scenario["rolling_std_5"] * (1.0 + volatility_delta_pct)).clip(lower=0.001)
        if "rolling_std_20" in X_scenario.columns:
            X_scenario["rolling_std_20"] = (X_scenario["rolling_std_20"] * (1.0 + volatility_delta_pct)).clip(lower=0.001)

        if "momentum_5" in X_scenario.columns:
            X_scenario["momentum_5"] = X_scenario["momentum_5"] * (1.0 + momentum_delta_pct)
        if "momentum_14" in X_scenario.columns:
            X_scenario["momentum_14"] = X_scenario["momentum_14"] * (1.0 + momentum_delta_pct)

        # Load Classification Model
        if model_id:
            model_run, model_instance = ModelRegistry.load_model_by_id(db, model_id)
        else:
            ticker_model = ModelRegistry.load_ticker_model(db, symbol)
            if ticker_model:
                model_run, model_instance = ticker_model
            else:
                try:
                    from app.models.trainer import ModelTrainerService
                    train_res = ModelTrainerService.train_ticker_model(db, symbol)
                    model_run, model_instance = ModelRegistry.load_model_by_id(db, train_res["model_id"])
                except Exception as train_err:
                    from app.core.logging import logger
                    logger.warning(f"Auto-training ticker model for {symbol} failed: {train_err}")
                    model_run = ModelRegistry.get_latest_approved_model(db, task_type="classification", symbol=symbol)
                    if not model_run:
                        raise ModelNotFoundException(f"No trained classification model found for ticker '{symbol}'.")
                    model_run, model_instance = ModelRegistry.load_model_by_id(db, model_run.id)

        model_features = [c for c in model_instance.feature_names if c in X_base.columns] if getattr(model_instance, "feature_names", None) else list(X_base.columns)
        X_base_aligned = X_base[model_features]
        X_scen_aligned = X_scenario[model_features]

        # Baseline Predictions
        base_pred_class = int(model_instance.predict(X_base_aligned)[0])
        base_probas = model_instance.predict_proba(X_base_aligned)
        base_prob_up = float(base_probas[0, 1]) if base_probas is not None else 0.5

        # Scenario Predictions
        scen_pred_class = int(model_instance.predict(X_scen_aligned)[0])
        scen_probas = model_instance.predict_proba(X_scen_aligned)
        scen_prob_up = float(scen_probas[0, 1]) if scen_probas is not None else 0.5

        # Regressors for returns
        reg_run = ModelRegistry.get_latest_approved_model(db, task_type="regression")
        base_ret = 0.005 if base_pred_class == 1 else -0.005
        scen_ret = 0.005 if scen_pred_class == 1 else -0.005
        if reg_run:
            try:
                _, reg_inst = ModelRegistry.load_model_by_id(db, reg_run.id)
                base_ret = float(reg_inst.predict(X_base)[0])
                scen_ret = float(reg_inst.predict(X_scenario)[0])
            except Exception:
                pass

        prob_delta = scen_prob_up - base_prob_up
        return_delta = scen_ret - base_ret

        # Risk comparison
        base_vol = float(X_base["volatility"].iloc[0]) if "volatility" in X_base.columns else 0.20
        scen_vol = float(X_scenario["volatility"].iloc[0]) if "volatility" in X_scenario.columns else 0.20
        base_risk = "HIGH" if base_vol > 0.35 else "MEDIUM" if base_vol > 0.20 else "LOW"
        scen_risk = "HIGH" if scen_vol > 0.35 else "MEDIUM" if scen_vol > 0.20 else "LOW"

        inputs_summary = {
            "market_return_delta_pct": round(market_return_delta * 100, 2),
            "volume_delta_pct": round(volume_delta_pct * 100, 2),
            "volatility_delta_pct": round(volatility_delta_pct * 100, 2),
            "momentum_delta_pct": round(momentum_delta_pct * 100, 2)
        }

        baseline_output = {
            "predicted_direction": "UP" if base_pred_class == 1 else "DOWN",
            "probability_up_pct": round(base_prob_up * 100, 1),
            "expected_return_pct": round(base_ret * 100, 2),
            "risk_level": base_risk
        }

        scenario_output = {
            "predicted_direction": "UP" if scen_pred_class == 1 else "DOWN",
            "probability_up_pct": round(scen_prob_up * 100, 1),
            "expected_return_pct": round(scen_ret * 100, 2),
            "risk_level": scen_risk
        }

        comparison = {
            "probability_up_delta_pct": round(prob_delta * 100, 1),
            "expected_return_delta_pct": round(return_delta * 100, 2),
            "direction_shifted": bool(base_pred_class != scen_pred_class)
        }

        # Persist Scenario
        scen_record = ScenarioRecord(
            stock_id=stock.id,
            model_run_id=model_run.id,
            inputs=inputs_summary,
            baseline_output=baseline_output,
            scenario_output=scenario_output
        )
        db.add(scen_record)
        db.commit()

        return {
            "symbol": stock.symbol,
            "company_name": stock.company_name,
            "data_cutoff": data_cutoff.strftime("%Y-%m-%d"),
            "model_metadata": {
                "model_id": model_run.id,
                "model_name": model_run.model_name,
                "model_version": model_run.model_version
            },
            "scenario_inputs": inputs_summary,
            "baseline": baseline_output,
            "scenario": scenario_output,
            "comparison": comparison,
            "assumptions": [
                "Linear and non-linear feature adjustments applied instantaneously to frozen cutoff state.",
                "Model assumes stationary relationship between engineered features and target direction.",
                "Results represent hypothetical model-based sensitivity, not causal market certainty."
            ],
            "disclaimer": "What-If Simulator evaluates hypothetical parameter sensitivity using statistical models. Not guaranteed future performance."
        }
