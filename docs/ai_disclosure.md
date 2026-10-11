# AI-Usage Disclosure

In accordance with Section 8 and Section 10 of the Hackathon Participant Guide, this document provides a full and transparent disclosure of the use of AI coding assistants during system development.

## 1. AI Coding Assistants Utilized
- **Assistant**: Google Antigravity AI Coding Assistant (powered by Google Gemini).
- **Scope**: Used as an interactive pair-programming and scaffolding partner throughout the build window.

## 2. Components Developed with AI Assistance & Verification Method

| Component / File | Generated Scope | Verification & Validation Methodology |
| :--- | :--- | :--- |
| **Synthetic Data Generator** (`data/generator.py`) | Physics-based simulation logic for 8 meters, product schedules, and tariff curves. | Validated against Annex B schemas; checked with Section 4.5 validation script (`data/validate_data.py`); inspected unmetered residual (3.66% $\le$ 7.0%). |
| **Data Validation Script** (`data/validate_data.py`) | Automated check of row counts, UTC regularity, non-negative bounds, and non-overlapping tariffs. | Executed across synthetic datasets and late-drop files; verified that edge cases and reset spikes are caught. |
| **Energy Baseline Model** (`src/analytics/baseline.py`) | Ordinary Least Squares (OLS) regression using NumPy. | Mathematically verified OLS formulation; tested $R^2 \ge 0.91$ and RMSE bounds using automated unit tests (`tests/test_baseline.py`). |
| **Cost Decomposition Engine** (`src/analytics/decomposition.py`) | Order of attribution solver and additivity reconciliation logic. | Validated strict additivity ($\sum \text{pct\_points} \equiv \text{total}$); checked against Annex A worked example; tested in `tests/test_decomposition.py`. |
| **Idle Load & Leak Detector** (`src/analytics/idle_waste.py`) | Off-shift baseload detection and night-to-day load ratio calculation. | Verified that Q3 night-time compressor load jumps to 35% of day load; confirmed fault location on Line 3. |
| **Prescriptive Engine** (`src/analytics/recommendations.py`) | Action ranking by payback period and bounded savings ranges. | Verified 100% of actions contain dual-bound ranges for kWh, money, and CO2e; verified payback ascending sort. |
| **API Server** (`src/api/main.py`) | FastAPI endpoints implementing Section 6 contract. | Tested using Pytest TestClient (`tests/test_api.py`); verified multipart file ingestion and Annex C trace retrieval. |
| **Number Faithfulness Verifier** (`src/agent/verifier.py`) | Regex numeric token parser and tool payload cross-referencer. | Tested adversarial hallucination injection cases in `tests/test_faithfulness.py`; verified 0 unauthorized figures bypass. |
| **Streamlit Web UI** (`src/ui/app.py`) | Interactive dashboard, Plotly waterfall charts, and what-if simulation controls. | Verified interactive controls, chart rendering, and live API communication. |

## 3. Human Engineering & Original Ownership
Every mathematical algorithm, attribution equation, and architecture decision was reviewed, tested, and validated by team members:
- All numbers and rankings originate strictly from deterministic Python solvers and analytical engines.
- No LLM hallucinations or hardcoded test mocks are used for calculations.
- Code has been verified with a 14-case unit test suite and a 22-case benchmark evaluation suite.
