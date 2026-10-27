import pandas as pd
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import ExplanationException, ModelNotFoundException
from app.data.repository import StockRepository
from app.features.pipeline import FeaturePipeline, FEATURE_COLUMNS
from app.models.registry import ModelRegistry
from app.explainability.feature_importance import get_global_feature_importance
from app.explainability.shap_explainer import compute_local_shap_values
from app.explainability.partial_dependence import compute_partial_dependence
from app.database.models import ExplanationRecord, PredictionRecord

class ExplainabilityEngine:
    @staticmethod
    def explain_prediction(
        db: Session,
        symbol: str,
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates full explainability suite: Global Feature Importance,
        Local SHAP Waterfall, Partial Dependence plots, and Natural Language synthesis.
        """
        stock = StockRepository.get_by_symbol(db, symbol)
        df_stock = StockRepository.get_price_history_df(db, symbol)

        df_market = None
        try:
            if symbol != "SPY":
                df_market = StockRepository.get_price_history_df(db, "SPY")
        except Exception:
            pass

        features_df = FeaturePipeline.generate_features_df(df_stock, df_market)
        X, y_dir, _, meta = FeaturePipeline.extract_ml_dataset(features_df)

        # Latest instance
        latest_row = features_df.iloc[-1]
        X_instance = pd.DataFrame([latest_row[FEATURE_COLUMNS].to_dict()]).fillna(0.0)

        # Load Model
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
                        raise ModelNotFoundException(f"No trained classification model found to explain for '{symbol}'.")
                    model_run, model_instance = ModelRegistry.load_model_by_id(db, model_run.id)

        # Feature alignment
        feature_cols = [c for c in model_instance.feature_names if c in latest_row] if getattr(model_instance, "feature_names", None) else FEATURE_COLUMNS
        X_instance = pd.DataFrame([latest_row[feature_cols].to_dict()]).fillna(0.0)
        X_bg = X[feature_cols] if all(c in X.columns for c in feature_cols) else X

        # 1. Global Feature Importance
        global_importance = get_global_feature_importance(model_instance)

        # 2. Local SHAP Attribution
        shap_res = compute_local_shap_values(
            model_instance=model_instance,
            X_instance=X_instance,
            X_background=X_bg.sample(min(100, len(X_bg)), random_state=42)
        )

        # 3. Partial Dependence for Top 2 Features
        top_feature_1 = global_importance[0]["feature"] if len(global_importance) > 0 else "momentum_5"
        top_feature_2 = global_importance[1]["feature"] if len(global_importance) > 1 else "volatility"

        pdp_1 = compute_partial_dependence(model_instance, X_bg.sample(min(150, len(X_bg)), random_state=42), top_feature_1)
        pdp_2 = compute_partial_dependence(model_instance, X_bg.sample(min(150, len(X_bg)), random_state=42), top_feature_2)

        # 4. Natural Language Synthesis
        top_pos = [item for item in shap_res["waterfall"] if item["impact"] == "POSITIVE"][:2]
        top_neg = [item for item in shap_res["waterfall"] if item["impact"] == "NEGATIVE"][:2]

        pos_text = ", ".join([f"{item['feature']} (+{item['shap_value']:.3f})" for item in top_pos]) if top_pos else "None"
        neg_text = ", ".join([f"{item['feature']} ({item['shap_value']:.3f})" for item in top_neg]) if top_neg else "None"

        nl_summary = (
            f"For {stock.symbol}, the model prediction is primarily driven upward by {pos_text}. "
            f"Conversely, downward pressure is exerted by {neg_text}. "
            f"Baseline probability across historical regimes is {shap_res['base_value']*100:.1f}%."
        )

        explanation_payload = {
            "symbol": stock.symbol,
            "company_name": stock.company_name,
            "model_metadata": {
                "model_id": model_run.id,
                "model_name": model_run.model_name,
                "model_version": model_run.model_version
            },
            "data_cutoff": latest_row["date"].strftime("%Y-%m-%d"),
            "global_feature_importance": global_importance,
            "shap_waterfall": shap_res["waterfall"],
            "base_value": shap_res["base_value"],
            "partial_dependence": {
                top_feature_1: pdp_1["points"],
                top_feature_2: pdp_2["points"]
            },
            "natural_language_summary": nl_summary
        }

        return explanation_payload
