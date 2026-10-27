# MarketMind Tech Stack

## Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query
- Zod
- Plotly.js / react-plotly.js
- Lucide React

## Backend
- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2
- Alembic
- Uvicorn

## Data & Mathematics
- Pandas
- NumPy
- SciPy

## Machine Learning
- scikit-learn
- SHAP
- joblib
Models: Logistic Regression, Linear/Multiple Regression, SVM, Decision Tree, Random Forest, K-Means, PCA.

## Database
- PostgreSQL 16+
- SQLAlchemy
- Alembic

## Testing
Frontend: Vitest, React Testing Library, Playwright.
Backend: Pytest, HTTPX, pytest-cov.
ML: deterministic seeds, leakage tests, chronological split tests, feature consistency tests.

## DevOps
Docker, Docker Compose, Git, GitHub, GitHub Actions.

## Services
frontend
backend
postgres
optional nginx reverse proxy.

## Rules
- Backend business logic stays out of routes.
- API calls stay out of presentational React components.
- ML preprocessing is reproducible.
- Dataset/feature/model versions are recorded.
- Backend timestamps use UTC.
- Final time-series evaluation is never randomly shuffled.
- No fake market data in real/demo flows.
