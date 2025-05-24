from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from memory.agents.dev_assistant import DevAssistantAgent

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/agent", response_class=HTMLResponse)
async def agent_ui(request: Request):
    return templates.TemplateResponse("agent.html", {
        "request": request,
        "title": "Smart Agent Assistant",
        "description": "Use natural language to command and modify your project in real-time."
    })

@router.post("/agent/update", response_class=JSONResponse)
async def run_instruction(request: Request):
    try:
        data = await request.json()
        instruction = data.get("instruction")
        agent = DevAssistantAgent()
        result = agent.process_agent_instruction(instruction)

        # Log the interaction
        from datetime import datetime
        import json
        from pathlib import Path

        log_entry = {
            "instruction": instruction,
            "result": result,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        log_path = Path("logs/agent_log.jsonl")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        return {"response": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})