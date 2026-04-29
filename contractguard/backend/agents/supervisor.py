from .state import ContractState, RiskFinding
from .payment_agent import PaymentAgent
from .liability_agent import LiabilityAgent

class SupervisorAgent:
    def __init__(self):
        self.payment_agent = PaymentAgent()
        self.liability_agent = LiabilityAgent()
        # 可扩展 ip_agent, confidentiality_agent

    def route_and_execute(self, state: ContractState) -> dict:
        text = state["contract_text"]
        clauses = state["extracted_clauses"]
        pay_findings = self.payment_agent.analyze(text, clauses)
        liab_findings = self.liability_agent.analyze(text, clauses)
        all_findings = pay_findings + liab_findings
        risk_summary = self._arbitrate(all_findings)
        return {
            "payment_findings": pay_findings,
            "liability_findings": liab_findings,
            "all_findings": all_findings,
            "risk_summary": risk_summary,
            "needs_human_review": risk_summary["high_risk_count"] >= 2
        }

    def _arbitrate(self, findings: list[RiskFinding]) -> dict:
        high = sum(1 for f in findings if f["risk_level"]=="high")
        medium = sum(1 for f in findings if f["risk_level"]=="medium")
        low = sum(1 for f in findings if f["risk_level"]=="low")
        score = high*10 + medium*5 + low
        overall_risk = "high" if high>=2 or score>=70 else "medium" if high>=1 or score>=40 else "low"
        return {"high_risk_count": high, "medium_risk_count": medium, "low_risk_count": low,
                "overall_score": min(100, score), "overall_risk": overall_risk}

    def generate_report(self, state: ContractState) -> str:
        summ = state["risk_summary"]
        lines = ["="*50, f"合同审阅报告 - {state['session_id']}", f"整体风险: {summ['overall_risk'].upper()} 评分: {summ['overall_score']}/100",
                 f"高风险: {summ['high_risk_count']} 中风险: {summ['medium_risk_count']} 低风险: {summ['low_risk_count']}", ""]
        for idx, f in enumerate(state["all_findings"], 1):
            lines.append(f"{idx}. [{f['risk_type']}] {f['risk_level']}")
            lines.append(f"   {f['description']}")
            lines.append(f"   建议: {f['suggestion']}\n")
        lines.append("免责: AI生成，仅供参考")
        return "\n".join(lines)