import joblib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import ModelNotFoundException
from app.database.models import ModelRun
from app.models.base import BaseModel

class ModelRegistry:
    @staticmethod
    def save_model(
        db: Session,
        model_instance: BaseModel,
        model_name: str,
        model_version: str,
        task_type: str,
        data_version_id: Optional[str],
        feature_version_id: Optional[str],
        training_start: Any,
        training_end: Any,
        validation_method: str,
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, Any],
        random_seed: int = 42
    ) -> ModelRun:
        """
        Saves serialized model artifact to disk and creates a ModelRun record in the database.
        """
        artifact_filename = f"{model_version}_{model_name.replace(' ', '_').lower()}.joblib"
        artifact_path = settings.MODEL_ARTIFACTS_DIR / artifact_filename
        model_instance.save(artifact_path)

        model_run = db.query(ModelRun).filter_by(model_version=model_version).first()
        if not model_run:
            model_run = ModelRun(
                model_name=model_name,
                model_version=model_version,
                task_type=task_type,
                data_version_id=data_version_id,
                feature_version_id=feature_version_id,
                training_start=training_start,
                training_end=training_end,
                validation_method=validation_method,
                hyperparameters=hyperparameters,
                metrics=metrics,
                random_seed=random_seed,
                artifact_uri=str(artifact_path),
                status="COMPLETED"
            )
            db.add(model_run)
        else:
            model_run.metrics = metrics
            model_run.hyperparameters = hyperparameters
            model_run.artifact_uri = str(artifact_path)

        db.commit()
        db.refresh(model_run)
        logger.info(f"Model '{model_name}' (version: {model_version}) registered successfully with ID {model_run.id}")
        return model_run

    @staticmethod
    def resolve_artifact_path(raw_path: str) -> Path:
        p = Path(raw_path)
        if p.exists():
            return p
        # Check in configured MODEL_ARTIFACTS_DIR
        candidate1 = settings.MODEL_ARTIFACTS_DIR / p.name
        if candidate1.exists():
            return candidate1
        # Check in models dir
        candidate2 = settings.BASE_DIR.parent / "models" / p.name
        if candidate2.exists():
            return candidate2
        # Check in models/artifacts
        candidate3 = settings.BASE_DIR.parent / "models" / "artifacts" / p.name
        if candidate3.exists():
            return candidate3
        return p

    @staticmethod
    def load_model_by_id(db: Session, model_run_id: str) -> Tuple[ModelRun, BaseModel]:
        model_run = db.query(ModelRun).filter_by(id=model_run_id).first()
        if not model_run:
            raise ModelNotFoundException(model_run_id)

        artifact_path = ModelRegistry.resolve_artifact_path(model_run.artifact_uri or model_run.artifact_filepath or "")
        if not artifact_path.exists():
            raise ModelNotFoundException(f"Artifact file missing at {artifact_path}")

        # Instantiate placeholder instance and load state
        from app.models.classification import (
            LogisticRegressionModel, SVMModel, DecisionTreeModel, RandomForestModel, HistGradientBoostingModel
        )
        from app.models.regression import LinearRegressionModel, RandomForestRegressorModel
        from app.models.baseline import MajorityClassBaseline, HistoricalMeanRegressorBaseline

        model_map = {
            "Histogram Gradient Boosting": HistGradientBoostingModel,
            "HistGradientBoostingClassifier": HistGradientBoostingModel,
            "Logistic Regression": LogisticRegressionModel,
            "Support Vector Machine": SVMModel,
            "Decision Tree": DecisionTreeModel,
            "Random Forest Classifier": RandomForestModel,
            "Linear Regression": LinearRegressionModel,
            "Random Forest Regressor": RandomForestRegressorModel,
            "Majority Class Baseline": MajorityClassBaseline,
            "Historical Mean Baseline": HistoricalMeanRegressorBaseline
        }

        cls = model_map.get(model_run.model_name, HistGradientBoostingModel)
        instance = cls()
        instance.load(artifact_path)
        return model_run, instance

    @staticmethod
    def load_ticker_model(db: Session, symbol: str) -> Optional[Tuple[ModelRun, BaseModel]]:
        """
        Dynamically locates and loads the specialized Ticker-Wise model artifact
        (e.g., model_{SYMBOL}.joblib or registered symbol model) with O(1) memory loading.
        """
        clean_sym = symbol.strip().upper()
        
        # 1. Check for dedicated model_{SYMBOL}.joblib on disk
        ticker_artifact_path = settings.MODEL_ARTIFACTS_DIR / f"model_{clean_sym}.joblib"
        if not ticker_artifact_path.exists():
            ticker_artifact_path = settings.MODEL_ARTIFACTS_DIR / f"model_{clean_sym}.pkl"

        if ticker_artifact_path.exists():
            from app.models.classification import HistGradientBoostingModel
            instance = HistGradientBoostingModel()
            instance.load(ticker_artifact_path)
            
            # Find or synthesize ModelRun
            model_run = db.query(ModelRun).filter(
                (ModelRun.ticker == clean_sym) | (ModelRun.model_version.contains(clean_sym.lower()))
            ).order_by(ModelRun.created_at.desc()).first()
            if not model_run:
                model_run = ModelRun(
                    ticker=clean_sym,
                    model_name=instance.name,
                    model_version=f"hgb_{clean_sym.lower()}_v1.0",
                    task_type="classification",
                    model_type="Histogram Gradient Boosting",
                    artifact_uri=str(ticker_artifact_path),
                    artifact_filepath=str(ticker_artifact_path),
                    status="COMPLETED"
                )
            return model_run, instance

        # 2. Check for registered model in DB for this specific ticker
        model_run = db.query(ModelRun).filter(
            (ModelRun.ticker == clean_sym) | (ModelRun.model_version.contains(clean_sym.lower())),
            ModelRun.task_type == "classification"
        ).order_by(ModelRun.created_at.desc()).first()

        if model_run:
            try:
                return ModelRegistry.load_model_by_id(db, model_run.id)
            except Exception as e:
                logger.warning(f"Failed loading DB registered model for {clean_sym}: {e}")

        return None

    @staticmethod
    def get_latest_approved_model(
        db: Session,
        task_type: str = "classification",
        symbol: Optional[str] = None
    ) -> Optional[ModelRun]:
        query = db.query(ModelRun).filter(ModelRun.task_type == task_type)
        if symbol:
            clean_sym = symbol.strip().upper()
            sym_query = query.filter(
                (ModelRun.ticker == clean_sym) | (ModelRun.model_version.contains(clean_sym.lower()))
            ).order_by(ModelRun.created_at.desc())
            res = sym_query.first()
            if res:
                return res

        return query.order_by(ModelRun.created_at.desc()).first()

    @staticmethod
    def list_all_models(db: Session) -> List[ModelRun]:
        return db.query(ModelRun).order_by(ModelRun.created_at.desc()).all()
