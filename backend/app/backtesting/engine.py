import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.core.exceptions import BacktestException, ModelNotFoundException
from app.data.repository import StockRepository
from app.features.pipeline import FeaturePipeline
from app.models.classification import (
    RandomForestModel, LogisticRegressionModel, SVMModel, DecisionTreeModel, HistGradientBoostingModel
)
from app.models.registry import ModelRegistry
from app.backtesting.splitter import ChronologicalWalkForwardSplitter
from app.backtesting.evaluator import evaluate_backtest_predictions
from app.database.models import BacktestRecord

class BacktestingEngine:
    @staticmethod
    def run_walk_forward_backtest(
        db: Session,
        symbol: str = "AAPL",
        model_name: str = "Random Forest Classifier",
        n_folds: int = 3
    ) -> Dict[str, Any]:
        """
        Executes a chronological walk-forward backtest across expanding training windows
        and evaluates out-of-sample directional accuracy, confusion matrices, and strategy returns.
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
        X, y_dir, y_ret, meta = FeaturePipeline.extract_ml_dataset(features_df)

        folds = ChronologicalWalkForwardSplitter.generate_walk_forward_folds(meta, n_folds=n_folds)

        fold_results = []
        all_series = []
        accuracies = []
        f1_scores = []

        model_cls_map = {
            "Histogram Gradient Boosting": HistGradientBoostingModel,
            "HistGradientBoostingClassifier": HistGradientBoostingModel,
            "Random Forest Classifier": RandomForestModel,
            "Logistic Regression": LogisticRegressionModel,
            "Support Vector Machine": SVMModel,
            "Decision Tree": DecisionTreeModel
        }
        cls_to_use = model_cls_map.get(model_name, HistGradientBoostingModel)

        for fold in folds:
            tr_start, tr_end = fold["train_indices"]
            te_start, te_end = fold["test_indices"]

            X_tr, y_tr = X.iloc[tr_start:tr_end], y_dir.iloc[tr_start:tr_end]
            X_te, y_te = X.iloc[te_start:te_end], y_dir.iloc[te_start:te_end]
            te_dates = meta["date"].iloc[te_start:te_end]
            te_rets = y_ret.iloc[te_start:te_end]

            # Fit fresh model instance on this fold's training portion ONLY
            fold_model = cls_to_use(random_state=42)
            fold_model.train(X_tr, y_tr)

            preds = fold_model.predict(X_te)
            probas = fold_model.predict_proba(X_te)

            eval_res = evaluate_backtest_predictions(
                dates=te_dates,
                actual_direction=y_te,
                predicted_direction=preds,
                predicted_proba=probas,
                actual_return=te_rets
            )

            accuracies.append(eval_res["accuracy"])
            f1_scores.append(eval_res["f1_score"])
            all_series.extend(eval_res["series"])

            fold_results.append({
                "fold_id": fold["fold_id"],
                "train_period": f"{fold['train_start_date']} to {fold['train_end_date']}",
                "test_period": f"{fold['test_start_date']} to {fold['test_end_date']}",
                "train_samples": fold["train_size"],
                "test_samples": fold["test_size"],
                "accuracy": eval_res["accuracy"],
                "precision": eval_res["precision"],
                "recall": eval_res["recall"],
                "f1_score": eval_res["f1_score"],
                "confusion_matrix": eval_res["confusion_matrix"],
                "strategy_return_pct": eval_res["total_strategy_return_pct"],
                "benchmark_return_pct": eval_res["total_benchmark_return_pct"]
            })

        mean_accuracy = round(float(np.mean(accuracies)), 4) if accuracies else 0.0
        mean_f1 = round(float(np.mean(f1_scores)), 4) if f1_scores else 0.0

        # Persist record
        latest_model = ModelRegistry.get_latest_approved_model(db, task_type="classification")
        model_run_id = latest_model.id if latest_model else "walk_forward_run"

        bt_record = BacktestRecord(
            model_run_id=model_run_id if latest_model else None,
            stock_id=stock.id,
            strategy="walk_forward_expanding",
            start_date=meta["date"].iloc[0],
            end_date=meta["date"].iloc[-1],
            metrics={"mean_accuracy": mean_accuracy, "mean_f1": mean_f1, "folds_count": len(folds)},
            fold_results=fold_results
        )
        if latest_model:
            db.add(bt_record)
            db.commit()
            db.refresh(bt_record)

        return {
            "backtest_id": bt_record.id,
            "symbol": stock.symbol,
            "company_name": stock.company_name,
            "model_name": model_name,
            "strategy": "Chronological Walk-Forward Expanding Windows",
            "total_folds": len(folds),
            "summary_metrics": {
                "mean_accuracy": mean_accuracy,
                "mean_f1_score": mean_f1,
                "min_accuracy": round(float(np.min(accuracies)), 4) if accuracies else 0.0,
                "max_accuracy": round(float(np.max(accuracies)), 4) if accuracies else 0.0
            },
            "fold_results": fold_results,
            "time_series_evaluation": all_series
        }
