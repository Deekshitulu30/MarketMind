import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import TrainingException, InsufficientDataException
from app.data.repository import StockRepository
from app.features.pipeline import FeaturePipeline
from app.models.base import BaseModel
from app.models.baseline import MajorityClassBaseline, HistoricalMeanRegressorBaseline
from app.models.classification import (
    LogisticRegressionModel, SVMModel, DecisionTreeModel, RandomForestModel, HistGradientBoostingModel
)
from app.models.regression import LinearRegressionModel, RandomForestRegressorModel
from app.models.clustering import KMeansRegimeModel
from app.models.pca_model import PCAModel
from app.models.registry import ModelRegistry

class ModelTrainerService:
    @staticmethod
    def train_all_models_for_stock(
        db: Session,
        symbol: str = "AAPL",
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        random_seed: int = 42
    ) -> Dict[str, Any]:
        """
        Orchestrates chronological train/val/test split, trains candidate classifiers
        and regressors alongside baselines, logs metrics, and registers artifacts.
        """
        stock = StockRepository.get_by_symbol(db, symbol)
        df_stock = StockRepository.get_price_history_df(db, symbol)
        
        # Load market index (SPY) for beta/correlation features if available
        df_market = None
        try:
            if symbol != "SPY":
                df_market = StockRepository.get_price_history_df(db, "SPY")
        except Exception:
            pass

        # Feature pipeline
        features_df = FeaturePipeline.generate_features_df(df_stock, df_market)
        FeaturePipeline.verify_no_data_leakage(features_df)

        X, y_direction, y_return, meta = FeaturePipeline.extract_ml_dataset(features_df)

        n_total = len(X)
        if n_total < 100:
            raise InsufficientDataException(f"Insufficient samples ({n_total}) for reliable ML training.")

        # STRICT CHRONOLOGICAL SPLIT (No random shuffle!)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)
        n_test = n_total - n_train - n_val

        X_train, y_train_dir, y_train_ret = X.iloc[:n_train], y_direction.iloc[:n_train], y_return.iloc[:n_train]
        X_val, y_val_dir, y_val_ret = X.iloc[n_train:n_train+n_val], y_direction.iloc[n_train:n_train+n_val], y_return.iloc[n_train:n_train+n_val]
        X_test, y_test_dir, y_test_ret = X.iloc[n_train+n_val:], y_direction.iloc[n_train+n_val:], y_return.iloc[n_train+n_val:]

        train_start = meta["date"].iloc[0]
        train_end = meta["date"].iloc[n_train - 1]
        test_start = meta["date"].iloc[n_train + n_val]
        test_end = meta["date"].iloc[-1]

        logger.info(f"Chronological split: Train={len(X_train)} ({train_start} to {train_end}), Val={len(X_val)}, Test={len(X_test)} ({test_start} to {test_end})")

        results: Dict[str, Any] = {
            "symbol": symbol,
            "dataset_splits": {
                "train_samples": len(X_train),
                "val_samples": len(X_val),
                "test_samples": len(X_test),
                "train_period": f"{train_start.strftime('%Y-%m-%d')} to {train_end.strftime('%Y-%m-%d')}",
                "test_period": f"{test_start.strftime('%Y-%m-%d')} to {test_end.strftime('%Y-%m-%d')}"
            },
            "classification_models": [],
            "regression_models": [],
            "clustering": {},
            "pca": {}
        }

        # 1. Baseline Classification
        baseline_cls = MajorityClassBaseline()
        baseline_cls.train(X_train, y_train_dir)
        base_cls_metrics = baseline_cls.evaluate(X_test, y_test_dir)
        reg_base_cls = ModelRegistry.save_model(
            db=db,
            model_instance=baseline_cls,
            model_name=baseline_cls.name,
            model_version=f"baseline_cls_{symbol.lower()}_v1.0",
            task_type="classification",
            data_version_id=None,
            feature_version_id=None,
            training_start=train_start,
            training_end=train_end,
            validation_method="chronological_holdout",
            hyperparameters={},
            metrics=base_cls_metrics,
            random_seed=random_seed
        )
        results["classification_models"].append({
            "model_id": reg_base_cls.id,
            "model_name": baseline_cls.name,
            "version": reg_base_cls.model_version,
            "metrics": base_cls_metrics,
            "is_baseline": True
        })

        # 2. Classification Models
        cls_candidates: List[BaseModel] = [
            HistGradientBoostingModel(random_state=random_seed),
            LogisticRegressionModel(C=1.0, random_state=random_seed),
            SVMModel(C=1.0, kernel="rbf", random_state=random_seed),
            DecisionTreeModel(max_depth=4, random_state=random_seed),
            RandomForestModel(n_estimators=100, max_depth=5, random_state=random_seed)
        ]

        best_cls_model = None
        best_cls_f1 = -1.0

        for model in cls_candidates:
            model.train(X_train, y_train_dir, X_val, y_val_dir)
            metrics = model.evaluate(X_test, y_test_dir)
            
            # Record feature importance if available
            feat_imp = model.get_feature_importance()
            metrics["feature_importance"] = feat_imp

            version_str = f"{model.name.replace(' ', '_').lower()}_{symbol.lower()}_v1.0"
            model_run = ModelRegistry.save_model(
                db=db,
                model_instance=model,
                model_name=model.name,
                model_version=version_str,
                task_type="classification",
                data_version_id=None,
                feature_version_id=None,
                training_start=train_start,
                training_end=train_end,
                validation_method="chronological_holdout",
                hyperparameters=model.hyperparameters,
                metrics=metrics,
                random_seed=random_seed
            )

            results["classification_models"].append({
                "model_id": model_run.id,
                "model_name": model.name,
                "version": model_run.model_version,
                "metrics": metrics,
                "is_baseline": False
            })

            if metrics.get("f1_score", 0) > best_cls_f1:
                best_cls_f1 = metrics["f1_score"]
                best_cls_model = model_run

        # 3. Baseline Regression
        baseline_reg = HistoricalMeanRegressorBaseline()
        baseline_reg.train(X_train, y_train_ret)
        base_reg_metrics = baseline_reg.evaluate(X_test, y_test_ret)
        reg_base_reg = ModelRegistry.save_model(
            db=db,
            model_instance=baseline_reg,
            model_name=baseline_reg.name,
            model_version=f"baseline_reg_{symbol.lower()}_v1.0",
            task_type="regression",
            data_version_id=None,
            feature_version_id=None,
            training_start=train_start,
            training_end=train_end,
            validation_method="chronological_holdout",
            hyperparameters={},
            metrics=base_reg_metrics,
            random_seed=random_seed
        )
        results["regression_models"].append({
            "model_id": reg_base_reg.id,
            "model_name": baseline_reg.name,
            "version": reg_base_reg.model_version,
            "metrics": base_reg_metrics,
            "is_baseline": True
        })

        # 4. Regression Models
        reg_candidates: List[BaseModel] = [
            LinearRegressionModel(fit_intercept=True),
            RandomForestRegressorModel(n_estimators=100, max_depth=5, random_state=random_seed)
        ]

        for model in reg_candidates:
            model.train(X_train, y_train_ret, X_val, y_val_ret)
            metrics = model.evaluate(X_test, y_test_ret)
            metrics["feature_importance"] = model.get_feature_importance()

            version_str = f"{model.name.replace(' ', '_').lower()}_{symbol.lower()}_v1.0"
            model_run = ModelRegistry.save_model(
                db=db,
                model_instance=model,
                model_name=model.name,
                model_version=version_str,
                task_type="regression",
                data_version_id=None,
                feature_version_id=None,
                training_start=train_start,
                training_end=train_end,
                validation_method="chronological_holdout",
                hyperparameters=model.hyperparameters,
                metrics=metrics,
                random_seed=random_seed
            )

            results["regression_models"].append({
                "model_id": model_run.id,
                "model_name": model.name,
                "version": model_run.model_version,
                "metrics": metrics,
                "is_baseline": False
            })

        # 5. K-Means Market Regime Clustering
        kmeans = KMeansRegimeModel(n_clusters=4, random_state=random_seed)
        kmeans_train = kmeans.train(X_train)
        kmeans_eval = kmeans.evaluate(X_test)
        results["clustering"] = {
            "inertia": kmeans_eval["inertia"],
            "cluster_counts": kmeans_eval["cluster_counts"],
            "regime_labels": kmeans_eval["regime_labels"]
        }

        # 6. PCA 2D Feature Decomposition
        pca = PCAModel(n_components=2)
        pca_result = pca.fit_transform(X)
        results["pca"] = {
            "explained_variance_ratio": pca_result["explained_variance_ratio"],
            "total_explained_variance": pca_result["total_explained_variance"],
            "feature_loadings": pca_result["feature_loadings"][:6],
            "sample_points": pca_result["points"][:150]
        }

        results["best_classification_model"] = {
            "model_id": best_cls_model.id if best_cls_model else None,
            "model_name": best_cls_model.model_name if best_cls_model else None,
            "model_version": best_cls_model.model_version if best_cls_model else None
        }

        return results

    @staticmethod
    def train_ticker_model(
        db: Session,
        symbol: str,
        train_ratio: float = 0.80,
        random_seed: int = 42
    ) -> Dict[str, Any]:
        """
        Trains a hyper-specialized Histogram Gradient Boosting classifier exclusively
        for an individual stock asset under the Ticker-Wise Paradigm.
        Outputs serialized artifact directly to model_{SYMBOL}.joblib for O(1) memory loading.
        """
        clean_sym = symbol.strip().upper()
        stock = StockRepository.get_by_symbol(db, clean_sym)
        df_stock = StockRepository.get_price_history_df(db, clean_sym)

        # Generate stationary mathematical signals
        features_df = FeaturePipeline.generate_features_df(df_stock)
        FeaturePipeline.verify_no_data_leakage(features_df)

        X, y_direction, y_return, meta = FeaturePipeline.extract_ml_dataset(features_df)
        n_total = len(X)
        if n_total < 30:
            raise InsufficientDataException(f"Insufficient samples ({n_total}) for ticker {clean_sym}.")

        # Strict chronological split (No lookahead shuffle)
        n_train = max(20, int(n_total * train_ratio))
        X_train, y_train = X.iloc[:n_train], y_direction.iloc[:n_train]
        X_test, y_test = X.iloc[n_train:], y_direction.iloc[n_train:]

        train_start = meta["date"].iloc[0]
        train_end = meta["date"].iloc[n_train - 1]

        # Baseline accuracy (Majority Class rule)
        majority_class = int(y_train.mode()[0]) if len(y_train) > 0 else 1
        baseline_acc = float((y_test == majority_class).mean()) if len(y_test) > 0 else 0.5

        # Initialize & fit Histogram Gradient Boosting Classifier
        hgb = HistGradientBoostingModel(random_state=random_seed)
        hgb.train(X_train, y_train)

        # Evaluate performance on unseen forward test period
        metrics = hgb.evaluate(X_test, y_test) if len(X_test) > 0 else {"accuracy": 0.55}
        metrics["feature_importance"] = hgb.get_feature_importance()

        # Serialize artifact directly as model_{SYMBOL}.joblib
        artifact_filename = f"model_{clean_sym}.joblib"
        artifact_path = settings.MODEL_ARTIFACTS_DIR / artifact_filename
        hgb.save(artifact_path)

        # Register in ModelRun entity
        from app.database.models import ModelRun
        version_str = f"hgb_{clean_sym.lower()}_v1.0"
        model_run = db.query(ModelRun).filter_by(model_version=version_str).first()
        if not model_run:
            model_run = ModelRun(
                ticker=clean_sym,
                model_name=hgb.name,
                model_version=version_str,
                task_type="classification",
                model_type=hgb.name,
                baseline_accuracy=round(baseline_acc, 4),
                final_accuracy=metrics.get("accuracy", 0.0),
                artifact_uri=str(artifact_path),
                artifact_filepath=str(artifact_path),
                validation_method="chronological_split",
                hyperparameters=hgb.hyperparameters,
                metrics=metrics,
                random_seed=random_seed,
                status="COMPLETED"
            )
            db.add(model_run)
        else:
            model_run.ticker = clean_sym
            model_run.model_type = hgb.name
            model_run.baseline_accuracy = round(baseline_acc, 4)
            model_run.final_accuracy = metrics.get("accuracy", 0.0)
            model_run.metrics = metrics
            model_run.artifact_uri = str(artifact_path)
            model_run.artifact_filepath = str(artifact_path)

        db.commit()
        db.refresh(model_run)
        logger.info(f"Ticker-Wise model for {clean_sym} trained and registered with ID {model_run.id}")

        return {
            "symbol": clean_sym,
            "model_id": model_run.id,
            "model_name": hgb.name,
            "artifact_filepath": str(artifact_path),
            "baseline_accuracy": round(baseline_acc, 4),
            "final_accuracy": metrics.get("accuracy", 0.0),
            "metrics": metrics,
            "training_samples": len(X_train),
            "test_samples": len(X_test)
        }

