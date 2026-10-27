from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import MarketMindException
from app.database.session import engine, Base, SessionLocal
from app.data.ingestion import DataIngestionService

# Import all API routes
from app.api.routes import (
    health,
    market,
    statistics,
    features,
    models,
    prediction,
    explainability,
    backtest,
    what_if,
    live_ws
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist & seed default data
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            if "sqlite" in str(engine.url):
                res = conn.execute(text("PRAGMA table_info(model_runs)")).fetchall()
                existing_cols = [r[1] for r in res]
                for col, typ in [
                    ("ticker", "TEXT"),
                    ("model_type", "TEXT"),
                    ("baseline_accuracy", "FLOAT"),
                    ("final_accuracy", "FLOAT"),
                    ("artifact_filepath", "TEXT")
                ]:
                    if col not in existing_cols:
                        conn.execute(text(f"ALTER TABLE model_runs ADD COLUMN {col} {typ}"))
                conn.commit()
    except Exception as col_err:
        logger.warning(f"Database column migration note: {col_err}")

    db: Session = SessionLocal()
    try:
        DataIngestionService.initialize_default_datasets(db)
    except Exception as e:
        logger.error(f"Error during default dataset seeding: {str(e)}")
    finally:
        db.close()

    logger.info(f"{settings.APP_NAME} API started successfully.")
    yield
    logger.info("Shutting down API...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Explainable Stock Market Intelligence & What-If Prediction Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for easy local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Structured Error Handler
@app.exception_handler(MarketMindException)
async def marketmind_exception_handler(request: Request, exc: MarketMindException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error processing {request.method} {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred.",
                "details": {"path": str(request.url)}
            }
        }
    )

# Include API Routers under /api/v1
api_prefix = settings.API_V1_STR
app.include_router(health.router, prefix=api_prefix, tags=["Health"])
app.include_router(health.router, tags=["Root Health"]) # Also available at /health
app.include_router(market.router, prefix=api_prefix, tags=["Market"])
app.include_router(statistics.router, prefix=api_prefix, tags=["Statistics"])
app.include_router(features.router, prefix=api_prefix, tags=["Features"])
app.include_router(models.router, prefix=api_prefix, tags=["Models"])
app.include_router(prediction.router, prefix=api_prefix, tags=["Prediction"])
app.include_router(prediction.router, prefix="/api", tags=["Prediction Direct"])
app.include_router(explainability.router, prefix=api_prefix, tags=["Explainability"])
app.include_router(backtest.router, prefix=api_prefix, tags=["Backtesting"])
app.include_router(what_if.router, prefix=api_prefix, tags=["What-If"])
app.include_router(live_ws.router, prefix=api_prefix, tags=["Live Streaming"])
app.include_router(live_ws.router, tags=["Root Live Streaming"])

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{api_prefix}/health",
        "disclaimer": "MarketMind is an educational and research-oriented platform. Not financial advice."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.BACKEND_HOST, port=settings.BACKEND_PORT, reload=True)
