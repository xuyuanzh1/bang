from typing import TypedDict, List, Dict, Optional
from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage

class RiskFinding(TypedDict):
    clause_id: str
    clause_text: str
    risk_type: str
    risk_level: str
    description: str
    suggestion: str
    confidence: float

class ContractState(TypedDict):
    session_id: str
    project_id: str
    contract_text: str
    extracted_clauses: Dict[str, str]
    messages: List[AnyMessage]
    payment_findings: List[RiskFinding]
    liability_findings: List[RiskFinding]
    ip_findings: List[RiskFinding]
    confidentiality_findings: List[RiskFinding]
    all_findings: List[RiskFinding]
    risk_summary: Dict
    current_agent: str
    remaining_steps: int
    needs_human_review: bool
    final_report: Optional[str]