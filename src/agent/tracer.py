"""
Execution Audit Tracer (R12 & Annex C).
Constructs and stores audit traces in DuckDB conforming strictly to Annex C schema.
"""

import uuid
from typing import Dict, Any, List, Optional
from src.database import db

class AuditTracer:
    def __init__(self):
        pass

    def generate_run_id(self) -> str:
        """Generates run_id formatted like 'en-5d20ab'."""
        short_hex = uuid.uuid4().hex[:6]
        return f"en-{short_hex}"

    def build_trace_record(
        self,
        run_id: str,
        question: str,
        steps: List[Dict[str, Any]],
        llm_calls: int = 1,
        tokens: int = 1600
    ) -> Dict[str, Any]:
        """Constructs Annex C compliant trace dictionary."""
        return {
            "run_id": run_id,
            "question": question,
            "steps": steps,
            "llm_calls": llm_calls,
            "tokens": tokens
        }

    def save_trace(self, run_id: str, question: str, answer_type: str, 
                   response_dict: Dict[str, Any], trace_dict: Dict[str, Any]):
        """Persists the trace record in the database."""
        db.record_trace(
            run_id=run_id,
            question=question,
            answer_type=answer_type,
            response_dict=response_dict,
            trace_dict=trace_dict
        )

    def get_trace(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves trace from database by run_id."""
        return db.get_trace(run_id)

audit_tracer = AuditTracer()
