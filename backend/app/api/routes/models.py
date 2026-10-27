import numpy as np
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.schemas.models import TrainModelsRequest, TrainModelsResponse, ModelRunSummary
from app.models.trainer import ModelTrainerService
from app.models.registry import ModelRegistry
from app.models.clustering import KMeansRegimeModel, REGIME_LABELS
from app.models.pca_model import PCAModel
from app.data.repository import StockRepository
from app.features.pipeline import FeaturePipeline
from app.database.models import ModelRun

router = APIRouter()

@router.post("/models/train", response_model=TrainModelsResponse)
def train_models(req: TrainModelsRequest, db: Session = Depends(get_db)):
    result = ModelTrainerService.train_all_models_for_stock(
        db=db,
        symbol=req.symbol.upper(),
        train_ratio=req.train_ratio,
        val_ratio=req.val_ratio,
        test_ratio=req.test_ratio,
        random_seed=req.random_seed
    )
    return result

@router.get("/models/regimes")
def get_market_regimes(symbol: str = "AAPL", db: Session = Depends(get_db)):
    clean_sym = symbol.strip().upper()
    df_stock = StockRepository.get_price_history_df(db, clean_sym)

    df_market = None
    try:
        if clean_sym != "SPY":
            df_market = StockRepository.get_price_history_df(db, "SPY")
    except Exception:
        pass

    features_df = FeaturePipeline.generate_features_df(df_stock, df_market)
    X, y_dir, y_ret, meta = FeaturePipeline.extract_ml_dataset(features_df)

    kmeans = KMeansRegimeModel(n_clusters=4, random_state=42)
    kmeans.train(X)
    cluster_preds = kmeans.predict(X)

    pca = PCAModel(n_components=2)
    pca_result = pca.fit_transform(X)

    # Calculate regime statistics
    regimes_list = []
    for cluster_id in range(4):
        mask = (cluster_preds == cluster_id)
        count = int(np.sum(mask))
        if count > 0:
            cluster_returns = y_ret[mask]
            m_ret = float(cluster_returns.mean())
            m_vol = float(cluster_returns.std() * (252 ** 0.5)) if len(cluster_returns) > 1 else 0.15
        else:
            m_ret = 0.0
            m_vol = 0.15

        regimes_list.append({
            "cluster_id": cluster_id,
            "regime_name": REGIME_LABELS.get(cluster_id, f"Regime {cluster_id}"),
            "sample_count": count,
            "mean_return": round(m_ret, 4),
            "mean_volatility": round(m_vol, 4)
        })

    return {
        "symbol": clean_sym,
        "n_clusters": 4,
        "explained_variance_ratio": pca_result["explained_variance_ratio"],
        "pca_points": pca_result["points"][:150],
        "regimes": regimes_list
    }

@router.get("/models")
def list_models(symbol: Optional[str] = None, db: Session = Depends(get_db)):
    all_models = ModelRegistry.list_all_models(db)
    clean_sym = symbol.strip().upper() if symbol else None

    if clean_sym:
        models = [m for m in all_models if (m.ticker == clean_sym or (m.model_version and clean_sym.lower() in m.model_version.lower()))]
        if not models:
            models = all_models
    else:
        models = all_models

    # Determine champion model by best accuracy
    best_id = None
    best_acc = -1.0
    for m in models:
        acc = (m.metrics or {}).get("accuracy", m.final_accuracy or 0.0)
        if acc > best_acc:
            best_acc = acc
            best_id = m.id

    model_summaries = [
        {
            "id": m.id,
            "model_name": m.model_name,
            "model_version": m.model_version,
            "task_type": m.task_type,
            "validation_method": m.validation_method or "chronological_split",
            "metrics": m.metrics or {},
            "validation_metrics": m.metrics or {},
            "test_accuracy": (m.metrics or {}).get("accuracy", m.final_accuracy or 0.0),
            "test_f1_score": (m.metrics or {}).get("f1_score", 0.0),
            "test_roc_auc": (m.metrics or {}).get("roc_auc", 0.0),
            "is_best_model": (m.id == best_id),
            "hyperparameters": m.hyperparameters or {},
            "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        }
        for m in models
    ]

    if clean_sym:
        return {
            "symbol": clean_sym,
            "models": model_summaries
        }
    return model_summaries

@router.get("/models/{model_id}")
def get_model_details(model_id: str, db: Session = Depends(get_db)):
    model_run, instance = ModelRegistry.load_model_by_id(db, model_id)
    return {
        "id": model_run.id,
        "model_name": model_run.model_name,
        "model_version": model_run.model_version,
        "task_type": model_run.task_type,
        "validation_method": model_run.validation_method,
        "hyperparameters": model_run.hyperparameters,
        "metrics": model_run.metrics,
        "feature_importance": instance.get_feature_importance(),
        "created_at": model_run.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
    }
