from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class MarketMindException(HTTPException):
    """Base application exception with structured error code and context."""
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": message,
                "details": details or {}
            }
        )
        self.error_code = error_code
        self.message = message
        self.details = details or {}

HTTP_422 = status.HTTP_422_UNPROCESSABLE_CONTENT if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT") else 422

class InvalidDataException(MarketMindException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("INVALID_DATA", message, HTTP_422, details)

class InvalidSymbolException(MarketMindException):
    def __init__(self, symbol: str):
        super().__init__("INVALID_SYMBOL", f"Stock symbol '{symbol}' was not found or is unsupported.", status.HTTP_404_NOT_FOUND, {"symbol": symbol})

class DataTemporarilyUnavailableException(MarketMindException):
    def __init__(self, symbol: str, retry_after: float = 30.0):
        super().__init__(
            "DATA_TEMPORARILY_UNAVAILABLE",
            f"Market data for symbol '{symbol}' is temporarily cooling down after repeated failures. Please retry in {int(retry_after)}s.",
            status.HTTP_503_SERVICE_UNAVAILABLE,
            {"symbol": symbol, "retry_after_seconds": round(retry_after, 1)}
        )

class InsufficientDataException(MarketMindException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("INSUFFICIENT_DATA", message, status.HTTP_400_BAD_REQUEST, details)

class ModelNotFoundException(MarketMindException):
    def __init__(self, model_id: str):
        super().__init__("MODEL_NOT_FOUND", f"Model '{model_id}' was not found in the registry.", status.HTTP_404_NOT_FOUND, {"model_id": model_id})

class DataLeakageException(MarketMindException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("DATA_LEAKAGE_DETECTED", message, status.HTTP_400_BAD_REQUEST, details)

class TrainingException(MarketMindException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("TRAINING_ERROR", message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)

class PredictionException(MarketMindException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("PREDICTION_ERROR", message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)

class BacktestException(MarketMindException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("BACKTEST_ERROR", message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)

class ExplanationException(MarketMindException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__("EXPLANATION_ERROR", message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)
