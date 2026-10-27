import time
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import PredictionException, ModelNotFoundException
from app.data.repository import StockRepository
from app.features.pipeline import FeaturePipeline, FEATURE_COLUMNS
from app.models.registry import ModelRegistry
from app.risk.engine import RiskEngine
from app.risk.reference_levels import calculate_atr, compute_model_reference_levels
from app.database.models import PredictionRecord, PredictionLog, ExplanationRecord
from app.explainability.shap_explainer import compute_local_shap_values

class PredictionService:
    @staticmethod
    def generate_prediction(
        db: Session,
        symbol: str,
        model_id: Optional[str] = None,
        horizon: int = 1,
        live_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generates probabilistic market direction prediction, expected return,
        TreeSHAP explainability, and educational risk evaluation under the Ticker-Wise Paradigm.
        """
        start_time = time.time()
        clean_sym = symbol.strip().upper()
        stock = StockRepository.get_by_symbol(db, clean_sym)
        df_stock = StockRepository.get_price_history_df(db, clean_sym)

        if live_price is not None and live_price > 0:
            df_stock = df_stock.copy()
            df_stock.iloc[-1, df_stock.columns.get_loc("close")] = live_price
            if "high" in df_stock.columns:
                df_stock.iloc[-1, df_stock.columns.get_loc("high")] = max(df_stock.iloc[-1]["high"], live_price)
            if "low" in df_stock.columns:
                df_stock.iloc[-1, df_stock.columns.get_loc("low")] = min(df_stock.iloc[-1]["low"], live_price)

        # Market index for market features if available
        df_market = None
        try:
            if clean_sym != "SPY":
                df_market = StockRepository.get_price_history_df(db, "SPY")
        except Exception:
            pass

        # Generate stationary features
        features_df = FeaturePipeline.generate_features_df(df_stock, df_market)
        
        # The latest row in features_df represents current state (cutoff date)
        latest_row = features_df.iloc[-1]
        cutoff_date = latest_row["date"]
        current_close = float(live_price if live_price is not None else latest_row["close"])

        # Dynamic Ticker-Wise Model Loading
        if model_id:
            model_run, model_instance = ModelRegistry.load_model_by_id(db, model_id)
        else:
            # 1. Locate dedicated Ticker-Wise model artifact
            ticker_model = ModelRegistry.load_ticker_model(db, clean_sym)
            if ticker_model:
                model_run, model_instance = ticker_model
            else:
                # 2. Check if model can be auto-trained for this ticker on demand
                try:
                    from app.models.trainer import ModelTrainerService
                    train_res = ModelTrainerService.train_ticker_model(db, clean_sym)
                    model_run, model_instance = ModelRegistry.load_model_by_id(db, train_res["model_id"])
                except Exception as train_err:
                    logger.warning(f"Auto-training ticker model for {clean_sym} failed: {train_err}")
                    model_run = ModelRegistry.get_latest_approved_model(db, task_type="classification", symbol=clean_sym)
                    if not model_run:
                        raise ModelNotFoundException(f"No trained classification model found for ticker '{clean_sym}'.")
                    model_run, model_instance = ModelRegistry.load_model_by_id(db, model_run.id)

        # Extract latest feature vector matching model's expected features
        model_features = [c for c in model_instance.feature_names if c in latest_row] if model_instance.feature_names else FEATURE_COLUMNS
        X_latest = pd.DataFrame([latest_row[model_features].to_dict()]).fillna(0.0)

        # Predict Direction & Probability
        direction_pred = int(model_instance.predict(X_latest)[0])
        predicted_class = "UP" if direction_pred == 1 else "DOWN"

        probabilities = model_instance.predict_proba(X_latest)
        if probabilities is not None and probabilities.shape[1] >= 2:
            prob_up = float(probabilities[0, 1])
            confidence_pct = round(prob_up * 100 if predicted_class == "UP" else (1.0 - prob_up) * 100, 1)
        else:
            prob_up = 0.5
            confidence_pct = 50.0

        # TreeSHAP Explainability in parallel
        try:
            shap_explanation = compute_local_shap_values(model_instance, X_latest)
        except Exception as e:
            logger.warning(f"TreeSHAP calculation fallback: {e}")
            shap_explanation = {"base_value": 0.5, "waterfall": []}

        # Load regressor for expected return if available
        reg_run = ModelRegistry.get_latest_approved_model(db, task_type="regression", symbol=clean_sym)
        expected_return = 0.005 if predicted_class == "UP" else -0.005
        if reg_run:
            try:
                _, reg_instance = ModelRegistry.load_model_by_id(db, reg_run.id)
                reg_features = [c for c in reg_instance.feature_names if c in latest_row] if reg_instance.feature_names else model_features
                X_reg = pd.DataFrame([latest_row[reg_features].to_dict()]).fillna(0.0)
                expected_return = float(reg_instance.predict(X_reg)[0])
                del reg_instance
            except Exception:
                pass

        predicted_price = round(current_close * (1 + expected_return), 2)

        # Calculate Risk Profile
        risk_profile = RiskEngine.calculate_risk_profile(df_stock["close"])

        # Calculate 14-day ATR for Educational Reference Levels
        high_series = df_stock["high"] if "high" in df_stock.columns else df_stock["close"]
        low_series = df_stock["low"] if "low" in df_stock.columns else df_stock["close"]
        atr_14 = calculate_atr(high_series, low_series, df_stock["close"], period=14)

        # Compute Model Reference Levels (Strict Educational Regulatory Framing)
        reference_levels = compute_model_reference_levels(
            last_close=current_close,
            expected_return=expected_return,
            predicted_direction=predicted_class,
            atr_value=atr_14,
            k_target_multiplier=1.5,
            m_stoploss_multiplier=1.0,
            model_version=model_run.model_version,
            confidence_pct=confidence_pct
        )

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # Persist prediction to PredictionRecord
        pred_record = PredictionRecord(
            model_run_id=model_run.id,
            stock_id=stock.id,
            data_cutoff=cutoff_date,
            horizon=horizon,
            predicted_class=predicted_class,
            probability_up=prob_up,
            predicted_return=round(expected_return, 6),
            predicted_price=predicted_price,
            risk_level=risk_profile["risk_level"]
        )
        db.add(pred_record)

        # Persist audit log to PredictionLog
        try:
            pred_log = PredictionLog(
                requested_ticker=stock.symbol,
                predicted_direction=predicted_class,
                confidence_score=confidence_pct,
                latency_ms=latency_ms
            )
            db.add(pred_log)
        except Exception as e:
            logger.warning(f"Could not persist to prediction_logs: {e}")

        db.commit()
        db.refresh(pred_record)

        # Stationary features snapshot for display
        features_snapshot = {
            "log_return": round(float(latest_row.get("log_return", 0.0)), 6),
            "volatility_5d": round(float(latest_row.get("volatility_5d", latest_row.get("rolling_std_5", 0.0))), 6),
            "volatility_20d": round(float(latest_row.get("volatility_20d", latest_row.get("rolling_std_20", 0.0))), 6),
            "c2h_ratio": round(float(latest_row.get("c2h_ratio", 0.5)), 4),
            "momentum_5": round(float(latest_row.get("momentum_5", 0.0)), 4),
            "momentum_14": round(float(latest_row.get("momentum_14", 0.0)), 4),
            "price_to_sma20": round(float(latest_row.get("price_to_sma20", 0.0)), 4)
        }

        # Clear model instance from active memory (O(1) memory loading)
        del model_instance

        return {
            "prediction_id": pred_record.id,
            "ticker": stock.symbol,
            "symbol": stock.symbol,
            "company_name": stock.company_name,
            "current_price": current_close,
            "data_cutoff": cutoff_date.strftime("%Y-%m-%d %H:%M"),
            "prediction_generated_at": pred_record.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "horizon_days": horizon,
            "predicted_direction": predicted_class,
            "probability_up": round(prob_up, 4),
            "probability_up_pct": round(prob_up * 100, 1),
            "confidence_score": confidence_pct,
            "confidence_pct": confidence_pct,
            "expected_return_pct": round(expected_return * 100, 2),
            "predicted_price": predicted_price,
            "latency_ms": latency_ms,
            "features": features_snapshot,
            "shap_values": shap_explanation,
            "risk_profile": risk_profile,
            "reference_levels": reference_levels,
            "model_metadata": {
                "model_id": model_run.id,
                "model_name": model_run.model_name,
                "model_version": model_run.model_version,
                "validation_accuracy": model_run.metrics.get("accuracy", 0.0),
                "architecture": "Ticker-Wise Isolated Classifier"
            },
            "disclaimer": "MarketMind prediction is generated by statistical/ML models for educational purposes. Not financial advice."
        }

