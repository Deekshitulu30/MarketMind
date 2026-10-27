# AGENTS.md — MarketMind

## Purpose
This document defines development rules for AI coding agents and human contributors working on MarketMind.

## Project Principles
1. Correctness over impressive-looking predictions.
2. Never claim that a prediction guarantees a market outcome.
3. Prevent data leakage.
4. Keep data, statistics, ML, API and UI concerns separated.
5. Make every experiment reproducible.
6. Prefer small, testable modules.
7. Document assumptions.

## Source-of-Truth Rules
- Product behavior: `docs/prd.md`
- Technical behavior: `docs/trd.md`
- System architecture: `docs/architecture.md`
- Architecture constraints: `docs/architecture-essentials.md`

When these documents conflict, stop and flag the conflict rather than silently choosing an interpretation.

## Coding Rules
### Python
- Use Python 3.11+ unless the project explicitly changes it.
- Add type hints to public functions.
- Keep functions focused.
- Avoid global mutable state.
- Use clear names.
- Add docstrings to reusable modules.
- Do not place business logic inside UI components.

### Data
- Validate schemas at ingestion.
- Never overwrite raw data.
- Preserve raw and processed layers separately.
- Version important feature definitions.
- Use deterministic transformations whenever possible.

### ML
- Every model must have a baseline.
- Every model run must record its dataset period and configuration.
- Time-dependent data must use chronological evaluation.
- Never fit preprocessing steps on the full dataset before splitting.
- Do not tune against the final test set.
- Report appropriate metrics rather than selecting a flattering metric.

### Statistics
- State the hypothesis before running a hypothesis test.
- Report assumptions where relevant.
- Do not interpret correlation as causation.
- Preserve units and scales.
- Explain missing-value and outlier handling.

### Visualization
- Choose charts based on the analytical question.
- Avoid misleading axes.
- Label units and dates.
- Show uncertainty where meaningful.
- Do not overload dashboards.
- Keep colors semantically consistent.
- Provide accessible labels/tooltips.

### API
- Validate request/response schemas.
- Return structured errors.
- Keep long-running training jobs out of synchronous request handlers if they become expensive.
- Never expose secrets.

### Security
- Never commit API keys, database passwords or tokens.
- Use `.env` locally and environment variables in deployment.
- Do not store real brokerage credentials.
- Do not implement real-money trading in MVP.

## Git Rules
Commit format:
```text
feat: add prediction endpoint
fix: prevent future leakage in rolling features
test: add backtest validation
docs: update architecture
refactor: split feature pipeline
```

Do not commit:
- `.env`
- credentials
- large raw datasets unless explicitly required
- generated model artifacts without project approval

## Testing Requirements
Before considering a feature complete:
1. Unit tests pass.
2. Relevant integration tests pass.
3. No leakage is introduced.
4. Documentation is updated if behavior changes.
5. Error paths are tested.

## Agent Workflow
1. Read relevant documentation.
2. Inspect existing implementation.
3. State the intended change.
4. Make the smallest coherent change.
5. Add/update tests.
6. Run tests.
7. Update documentation.
8. Summarize changed files and verification.

## Do Not
- Invent financial data.
- Present simulated results as real results.
- Claim model accuracy without evaluation.
- Randomly shuffle time-series data for final evaluation.
- Add libraries without explaining why they are needed.
- Rewrite unrelated modules.
