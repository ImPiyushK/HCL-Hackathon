import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.agent.graph import run_agent
from src.agent.tracer import audit_tracer

TRACES_DIR = os.path.join(os.path.dirname(__file__), "traces")
os.makedirs(TRACES_DIR, exist_ok=True)

# 1. Decomposition trace
res_decomp = run_agent("Why did the bill go up 15%?")
trace_decomp = audit_tracer.get_trace(res_decomp["run_id"])
with open(os.path.join(TRACES_DIR, "trace_decomposition.json"), "w") as f:
    json.dump(trace_decomp, f, indent=2)

# 2. Recommendation trace
res_rec = run_agent("What should we do first?")
trace_rec = audit_tracer.get_trace(res_rec["run_id"])
with open(os.path.join(TRACES_DIR, "trace_recommendation.json"), "w") as f:
    json.dump(trace_rec, f, indent=2)

# 3. Calculated trace
res_calc = run_agent("Which assets use the most energy?")
trace_calc = audit_tracer.get_trace(res_calc["run_id"])
with open(os.path.join(TRACES_DIR, "trace_calculated.json"), "w") as f:
    json.dump(trace_calc, f, indent=2)

print("Saved 3 sample trace records successfully to docs/traces/!")
