from .base_agent import BaseAgent
from .state import RiskFinding
import json

class PaymentAgent(BaseAgent):
    def analyze(self, contract_text: str, clauses: dict) -> list[RiskFinding]:
        payment_clause = clauses.get("付款条款", "") or self._locate(contract_text)
        if not payment_clause:
            return [self._missing_clause_finding()]
        prompt = """你是合同审阅专家。分析以下付款条款，输出JSON数组，每个元素包含 risk_level(high/medium/low), description, suggestion, confidence(0-1)。风险类型：付款期限不明、条件苛刻、预付款过大等。条款：""" + payment_clause
        resp = self.call_llm("输出JSON", prompt)
        try:
            items = json.loads(resp)
            return [{
                "clause_id": f"pay_{i}",
                "clause_text": payment_clause[:300],
                "risk_type": "payment",
                "risk_level": it["risk_level"],
                "description": it["description"],
                "suggestion": it["suggestion"],
                "confidence": it["confidence"]
            } for i, it in enumerate(items)]
        except:
            return [self._fallback(payment_clause, resp)]
    def _locate(self, text: str) -> str:
        for kw in ["付款", "支付", "价款"]:
            if kw in text:
                idx = text.lower().find(kw)
                return text[idx: idx+800]
        return ""
    def _missing_clause_finding(self):
        return {"clause_id":"pay_missing","clause_text":"","risk_type":"payment","risk_level":"high","description":"缺少付款条款","suggestion":"补充付款金额、时间、方式","confidence":0.85}
    def _fallback(self, clause, resp):
        return {"clause_id":"pay_fb","clause_text":clause[:300],"risk_type":"payment","risk_level":"medium","description":resp[:200],"suggestion":"人工复核","confidence":0.6}