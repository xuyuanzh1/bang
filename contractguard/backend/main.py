from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
from .parsers.pdf_parser import PDFParser
from .agents.graph import contract_graph
from .config import settings

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
parser = PDFParser()

@app.get("/")
async def root():
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>ContractGuard API</h1>")

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "仅支持PDF")
    content = await file.read()
    parsed = parser.parse_from_bytes(content)
    init_state = {
        "session_id": str(uuid.uuid4()),
        "project_id": "demo",
        "contract_text": parsed["full_text"],
        "extracted_clauses": parsed["extracted_clauses"],
        "messages": [],
        "payment_findings": [], "liability_findings": [], "ip_findings": [], "confidentiality_findings": [],
        "all_findings": [], "risk_summary": {}, "current_agent": "init", "remaining_steps": 5,
        "needs_human_review": False, "final_report": None
    }
    final = contract_graph.invoke(init_state, {"recursion_limit": 50})
    return {"success": True, "session_id": final["session_id"], "report": final["final_report"],
            "risk_summary": final["risk_summary"], "findings": final["all_findings"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)