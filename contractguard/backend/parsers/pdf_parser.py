import pymupdf
import io

class PDFParser:
    def parse_from_bytes(self, file_bytes: bytes):
        doc = pymupdf.open(stream=io.BytesIO(file_bytes), filetype="pdf")
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        clauses = self._extract_clauses(full_text)
        return {"full_text": full_text, "page_count": len(list(doc)), "extracted_clauses": clauses}
    def _extract_clauses(self, text):
        clauses = {}
        patterns = {"付款条款": ["付款","支付"], "违约责任": ["违约","逾期"]}
        for name, kws in patterns.items():
            for kw in kws:
                if kw in text:
                    idx = text.lower().find(kw)
                    clauses[name] = text[idx: idx+500]
                    break
        return clauses