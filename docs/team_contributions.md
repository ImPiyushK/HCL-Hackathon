# Team Contribution Statement

**Team Name**: Ninjas In Pyjamas (NIP)  
**Hackathon**: HCLTech Future Ready AI Engineer Hackathon  
**Track**: Factory Energy Cost Decomposition and Savings Agent  

---

## Team Roster & Modular Ownership

| Member | Primary Role | Modules & Components Built | Key Achievements |
| :--- | :--- | :--- | :--- |
| **Member 1 (Lead AI & Systems Engineer)** | Core Orchestration & API | `src/agent/graph.py`, `src/api/main.py`, `src/api/schemas.py`, `src/agent/tracer.py` | Built LangGraph state graph pipeline; implemented Section 6 FastAPI contract; engineered Annex C trace logging; Docker packaging. |
| **Member 2 (Analytics & Modeling Engineer)** | Mathematical Solvers & Decomposition | `src/analytics/baseline.py`, `src/analytics/decomposition.py`, `src/analytics/what_if.py` | Developed NumPy OLS regression ($R^2 \ge 0.91$); implemented Annex A Order of Attribution solver and strict Additivity math. |
| **Member 3 (Diagnostics & Data Engineer)** | Data Synthesis & Diagnostics | `data/generator.py`, `data/validate_data.py`, `data/loader.py`, `src/analytics/idle_waste.py` | Synthesized 140,544-row Annex B dataset with all edge cases; created Section 4.5 validation script; built compressor leak detector. |
| **Member 4 (Evaluation & Full-Stack UI)** | Prescriptive Engine & UI & Benchmarks | `src/analytics/recommendations.py`, `src/agent/verifier.py`, `src/ui/app.py`, `eval/run_eval.py` | Designed Streamlit Plotly waterfall dashboard; implemented Number Faithfulness verifier; ran 22-case benchmark evaluation suite. |

---

## Cross-Functional Competency
In accordance with Section 9.4 (Individual Assessment):
- Every team member understands the complete end-to-end dataflow from raw 15-minute interval readings through regression, attribution, verification, and UI visualization.
- Each member is prepared to answer questions during the live judge Q&A and implement real-time modifications if requested.
