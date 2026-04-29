from langgraph.graph import StateGraph, END
from .state import ContractState
from .supervisor import SupervisorAgent

def build_graph():
    supervisor = SupervisorAgent()
    workflow = StateGraph(ContractState)

    def parse(state):
        return {"current_agent": "parser"}

    def review_payment(state):
        res = supervisor.route_and_execute(state)
        return {"payment_findings": res["payment_findings"], "liability_findings": res["liability_findings"],
                "all_findings": res["all_findings"], "risk_summary": res["risk_summary"]}

    def generate(state):
        report = supervisor.generate_report(state)
        return {"final_report": report}

    workflow.add_node("parse", parse)
    workflow.add_node("review", review_payment)
    workflow.add_node("generate", generate)
    workflow.set_entry_point("parse")
    workflow.add_edge("parse", "review")
    workflow.add_edge("review", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()

contract_graph = build_graph()