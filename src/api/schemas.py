"""
Pydantic v2 Schemas for Mandatory API Contract (Section 6).
"""

from typing import List, Optional, Tuple, Literal
from pydantic import BaseModel, Field

AnswerType = Literal[
    "decomposition",
    "recommendation",
    "calculated",
    "not_in_data",
    "clarification_needed",
    "refused"
]

class AnalyzeRequest(BaseModel):
    question: str = Field(..., description="Natural language question or request")
    period: Optional[str] = Field("2026-Q3", description="Target period, e.g. '2026-Q3'")
    compare_to: Optional[str] = Field("2026-Q2", description="Baseline comparison period, e.g. '2026-Q2'")

class BridgeItem(BaseModel):
    cause: str
    pct_points: float
    range: List[float] = Field(..., description="[low, high] percentage points range")

class RecommendationItem(BaseModel):
    action: str
    saving_kwh_per_year: List[float]
    saving_money_per_year: List[float]
    saving_co2e_t_per_year: List[float]
    payback_months: List[float]
    ease: Literal["easy", "medium", "hard"]
    rationale: str
    evidence_refs: List[str]
    confidence: Literal["high", "medium", "low"]
    requires_approval: bool = True

class AnalyzeResponse(BaseModel):
    run_id: str
    answer_type: AnswerType
    summary: str
    bridge: Optional[List[BridgeItem]] = None
    recommendations: Optional[List[RecommendationItem]] = None
    assumptions: List[str] = Field(default_factory=lambda: ["Emission factor 0.4 kg CO2e per kWh"])
    limitations: List[str] = Field(default_factory=lambda: ["Weather effect estimated from one quarter of hot days"])

class IngestResponse(BaseModel):
    rows_loaded: int
    rows_rejected: int
    status: str

class HealthResponse(BaseModel):
    status: str
    database: str
    llm: str
    tables: dict

class StepRecord(BaseModel):
    agent: str
    tool: str
    output: Optional[dict] = None
    check: Optional[str] = None

class TraceResponse(BaseModel):
    run_id: str
    question: str
    steps: List[dict]
    llm_calls: int
    tokens: int
