from .base_agent import BaseAgent
import json

class LiabilityAgent(BaseAgent):
    def analyze(self, contract_text: str, clauses: dict):
        liab = clauses.get("违约责任", "") or self._locate(contract_text)
        if not liab:
            return [{"clause_id":"liab_missing","clause_text":"","risk_type":"liability","risk_level":"high","description":"缺失违约责任条款","suggestion":"补充违约情形和赔偿标准","confidence":0.85}]
        prompt = "输出JSON数组，分析违约责任条款：违约金过高、不对等、定义模糊等。" + liab
        resp = self.call_llm("输出JSON", prompt)
        try:
            items = json.loads(resp)
            return [{
                "clause_id": f"liab_{i}",
                "clause_text": liab[:300],
                "risk_type": "liability",
                "risk_level": it["risk_level"],
                "description": it["description"],
                "suggestion": it["suggestion"],
                "confidence": it["confidence"]
            } for i,it in enumerate(items)]
        except:
            return [{"clause_id":"liab_fb","clause_text":liab[:300],"risk_type":"liability","risk_level":"medium","description":resp[:200],"suggestion":"人工复核","confidence":0.6}]
    def _locate(self, text: str) -> str:
        for kw in ["违约", "逾期", "赔偿"]:
            if kw in text:
                idx = text.lower().find(kw)
                return text[idx: idx+800]
        return ""