import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, DateTime, ForeignKey, JSON, UniqueConstraint, Text
)
from sqlalchemy.orm import relationship
from app.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    symbol = Column(String(32), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    exchange = Column(String(64), nullable=False, default="NASDAQ")
    currency = Column(String(16), nullable=False, default="USD")
    sector = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prices = relationship("MarketPrice", back_populates="stock", cascade="all, delete-orphan")
    features = relationship("FeatureRecord", back_populates="stock", cascade="all, delete-orphan")
    predictions = relationship("PredictionRecord", back_populates="stock", cascade="all, delete-orphan")
    backtests = relationship("BacktestRecord", back_populates="stock", cascade="all, delete-orphan")

class DataVersion(Base):
    __tablename__ = "data_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False, unique=True)
    source = Column(String(255), nullable=False)
    checksum = Column(String(128), nullable=True)
    row_count = Column(Integer, default=0)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prices = relationship("MarketPrice", back_populates="data_version")
    model_runs = relationship("ModelRun", back_populates="data_version")

class FeatureVersion(Base):
    __tablename__ = "feature_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False)
    version = Column(String(64), nullable=False, unique=True)
    definition_hash = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    features = relationship("FeatureRecord", back_populates="feature_version")
    model_runs = relationship("ModelRun", back_populates="feature_version")

class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(String(36), ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    adjusted_close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    source = Column(String(64), default="CSV")
    data_version_id = Column(String(36), ForeignKey("data_versions.id"), nullable=True)

    stock = relationship("Stock", back_populates="prices")
    data_version = relationship("DataVersion", back_populates="prices")

    __table_args__ = (
        UniqueConstraint("stock_id", "timestamp", name="uq_stock_timestamp"),
    )

class FeatureRecord(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(String(36), ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    feature_version_id = Column(String(36), ForeignKey("feature_versions.id"), nullable=True)
    daily_return = Column(Float, nullable=True)
    log_return = Column(Float, nullable=True)
    rolling_mean_5 = Column(Float, nullable=True)
    rolling_mean_20 = Column(Float, nullable=True)
    rolling_std_5 = Column(Float, nullable=True)
    rolling_std_20 = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)
    momentum_5 = Column(Float, nullable=True)
    momentum_14 = Column(Float, nullable=True)
    volume_change = Column(Float, nullable=True)
    rolling_volume_20 = Column(Float, nullable=True)
    market_return = Column(Float, nullable=True)
    market_correlation = Column(Float, nullable=True)
    lag_1_return = Column(Float, nullable=True)
    lag_2_return = Column(Float, nullable=True)
    lag_5_return = Column(Float, nullable=True)

    stock = relationship("Stock", back_populates="features")
    feature_version = relationship("FeatureVersion", back_populates="features")

    __table_args__ = (
        UniqueConstraint("stock_id", "timestamp", "feature_version_id", name="uq_stock_time_featver"),
    )

class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticker = Column(String(32), nullable=True, index=True)
    model_type = Column(String(128), nullable=True)
    baseline_accuracy = Column(Float, nullable=True)
    final_accuracy = Column(Float, nullable=True)
    artifact_filepath = Column(String(512), nullable=True)
    model_name = Column(String(128), nullable=False)
    model_version = Column(String(64), nullable=False, unique=True)
    task_type = Column(String(64), nullable=False)  # classification / regression / clustering
    data_version_id = Column(String(36), ForeignKey("data_versions.id"), nullable=True)
    feature_version_id = Column(String(36), ForeignKey("feature_versions.id"), nullable=True)
    training_start = Column(DateTime, nullable=True)
    training_end = Column(DateTime, nullable=True)
    validation_method = Column(String(128), default="chronological_split")
    hyperparameters = Column(JSON, default=dict)
    metrics = Column(JSON, default=dict)
    random_seed = Column(Integer, default=42)
    artifact_uri = Column(String(512), nullable=True)
    status = Column(String(32), default="COMPLETED")
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def model_run_id(self):
        return self.id

    data_version = relationship("DataVersion", back_populates="model_runs")
    feature_version = relationship("FeatureVersion", back_populates="model_runs")
    predictions = relationship("PredictionRecord", back_populates="model_run", cascade="all, delete-orphan")
    backtests = relationship("BacktestRecord", back_populates="model_run", cascade="all, delete-orphan")

class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_run_id = Column(String(36), ForeignKey("model_runs.id"), nullable=False, index=True)
    stock_id = Column(String(36), ForeignKey("stocks.id"), nullable=False, index=True)
    data_cutoff = Column(DateTime, nullable=False)
    horizon = Column(Integer, default=1)
    predicted_class = Column(String(32), nullable=True)  # UP / DOWN
    probability_up = Column(Float, nullable=True)
    predicted_return = Column(Float, nullable=True)
    predicted_price = Column(Float, nullable=True)
    risk_level = Column(String(32), nullable=True)  # LOW / MEDIUM / HIGH
    created_at = Column(DateTime, default=datetime.utcnow)

    model_run = relationship("ModelRun", back_populates="predictions")
    stock = relationship("Stock", back_populates="predictions")
    explanation = relationship("ExplanationRecord", back_populates="prediction", uselist=False, cascade="all, delete-orphan")

class ExplanationRecord(Base):
    __tablename__ = "explanations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    prediction_id = Column(String(36), ForeignKey("predictions.id"), nullable=False, unique=True)
    method = Column(String(64), nullable=False)  # SHAP / FEATURE_IMPORTANCE
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    prediction = relationship("PredictionRecord", back_populates="explanation")

class BacktestRecord(Base):
    __tablename__ = "backtests"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_run_id = Column(String(36), ForeignKey("model_runs.id"), nullable=False)
    stock_id = Column(String(36), ForeignKey("stocks.id"), nullable=False)
    strategy = Column(String(128), default="walk_forward")
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    metrics = Column(JSON, default=dict)
    fold_results = Column(JSON, default=list)
    artifact_uri = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    model_run = relationship("ModelRun", back_populates="backtests")
    stock = relationship("Stock", back_populates="backtests")

class ScenarioRecord(Base):
    __tablename__ = "scenarios"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    stock_id = Column(String(36), ForeignKey("stocks.id"), nullable=False)
    model_run_id = Column(String(36), ForeignKey("model_runs.id"), nullable=False)
    baseline_prediction_id = Column(String(36), nullable=True)
    inputs = Column(JSON, nullable=False)
    baseline_output = Column(JSON, nullable=False)
    scenario_output = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(32), nullable=False, index=True)
    date_utc = Column(DateTime, nullable=False, index=True)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("ticker", "date_utc", name="uq_stock_price_ticker_date"),
    )

class FeatureSet(Base):
    __tablename__ = "feature_sets"

    feature_set_id = Column(String(36), primary_key=True, default=generate_uuid)
    ticker = Column(String(32), nullable=False, index=True)
    date_utc = Column(DateTime, nullable=False, index=True)
    log_return = Column(Float, nullable=True)
    volatility_5d = Column(Float, nullable=True)
    volatility_20d = Column(Float, nullable=True)
    momentum_ratio = Column(Float, nullable=True)
    c2h_ratio = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    log_id = Column(String(36), primary_key=True, default=generate_uuid)
    requested_ticker = Column(String(32), nullable=False, index=True)
    predicted_direction = Column(String(16), nullable=False)  # UP / DOWN
    confidence_score = Column(Float, nullable=False)
    latency_ms = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

