from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TrainModelsRequest(BaseModel):
    symbol: str = Field("AAPL")
    train_ratio: float = Field(0.70, ge=0.5, le=0.85)
    val_ratio: float = Field(0.15, ge=0.05, le=0.25)
    test_ratio: float = Field(0.15, ge=0.05, le=0.25)
    random_seed: int = Field(42)

class ModelRunSummary(BaseModel):
    id: str
    model_name: str
    model_version: str
    task_type: str
    validation_method: str
    metrics: Dict[str, Any]
    hyperparameters: Dict[str, Any]
    created_at: str

class TrainModelsResponse(BaseModel):
    symbol: str
    dataset_splits: Dict[str, Any]
    classification_models: List[Dict[str, Any]]
    regression_models: List[Dict[str, Any]]
    clustering: Dict[str, Any]
    pca: Dict[str, Any]
    best_classification_model: Dict[str, Any]
