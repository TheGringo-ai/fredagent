import csv
import json
import logging
from io import StringIO
from pathlib import Path

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from web.memory.agents.control_center import ControlCenter
from web.memory.memory_manager import MemoryManager
from web.memory.summarizer import Summarizer
from web.utils.response import success_response, error_response

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "web" / "templates"))

control_agent = ControlCenter()
memory = MemoryManager()

summarizer = Summarizer()

@router.get("/", response_class=HTMLResponse)
async def control_form(request: Request):
    allowed_extensions = {".md", ".txt"}
    files = [str(p.relative_to(BASE_DIR)) for p in (BASE_DIR / "dev_docs").rglob("*") if p.is_file() and p.suffix in allowed_extensions]
    readme = next((f for f in files if f.endswith("README.md")), None)
    return templates.TemplateResponse("control.html", {
        "request": request,
        "available_files": files,
        "readme_path": readme
    })

@router.post("/run", response_class=JSONResponse)
async def run_instruction(request: Request, instruction: str = Form(...)):
    client_ip = request.client.host
    logger.info(f"Instruction received from {client_ip}: {instruction}")
    try:
        result = control_agent.run(instruction)
        return success_response({"output": result})
    except Exception as e:
        return error_response(str(e), status_code=500)

@router.post("/search_memory", response_class=JSONResponse)
async def search_memory(request: Request, query: str = Form(...), intent: str = Form("")):
    try:
        matches = memory.search_by_summary(query, top_k=10)
        if intent:
            matches = [m for m in matches if m.get("intent", "") == intent.lower()]
        return success_response({"results": matches})
    except Exception as e:
        return error_response(str(e), status_code=500)

@router.post("/memory/search", response_class=JSONResponse)
async def vector_memory_search(request: Request, query: str = Form(...), intent: str = Form(""), top_k: int = Form(10)):
    try:
        matches = memory.search_by_summary(query, top_k=top_k)
        if intent:
            matches = [m for m in matches if m.get("intent", "") == intent.lower()]
        return success_response({"results": matches})
    except Exception as e:
        return error_response(str(e), status_code=500)

@router.get("/export_logs")
async def export_logs(request: Request, format: str = "json"):
    try:
        log_path = BASE_DIR / "logs" / "user_log.jsonl"
        with open(log_path, "r", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f]

        if format == "csv":
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=lines[0].keys())
            writer.writeheader()
            writer.writerows(lines)
            output.seek(0)
            return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=logs.csv"})
        else:
            output = json.dumps(lines, indent=2)
            return StreamingResponse(StringIO(output), media_type="application/json", headers={"Content-Disposition": "attachment; filename=logs.json"})

    except Exception as e:
        return error_response(str(e), status_code=500)

@router.post("/memory/summarize", response_class=JSONResponse)
async def memory_summarize(request: Request, query: str = Form(...), intent: str = Form("")):
    try:
        matches = memory.search_by_summary(query, top_k=10)
        if intent:
            matches = [m for m in matches if m.get("intent", "") == intent.lower()]
        combined = "\n".join([m["summary"] for m in matches])
        summary = summarizer.summarize(combined)
        return success_response({"results": matches, "summary": summary})
    except Exception as e:
        return error_response(str(e), status_code=500)