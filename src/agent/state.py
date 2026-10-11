"""
LangGraph Agent State Schema.
Defines the state passed between nodes in the orchestration workflow.
"""

from typing import Dict, Any, List, Optional, TypedDict

class AgentState(TypedDict):
    run_id: str
    question: str
    period: str
    compare_to: str
    answer_type: str  # decomposition | recommendation | calculated | not_in_data | clarification_needed | refused
    tool_outputs: Dict[str, Any]
    steps_trace: List[Dict[str, Any]]
    summary: str
    bridge: Optional[List[Dict[str, Any]]]
    recommendations: Optional[List[Dict[str, Any]]]
    assumptions: List[str]
    limitations: List[str]
    faithfulness_check: Dict[str, Any]
    llm_calls: int
    tokens: int
    error: Optional[str]
