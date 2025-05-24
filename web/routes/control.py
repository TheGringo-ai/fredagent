

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from memory.agents.control_center import ControlCenter

router = APIRouter()
templates = Jinja2Templates(directory="web/templates")

control_agent = ControlCenter()

@router.get("/", response_class=HTMLResponse)
async def control_form(request: Request):
    return templates.TemplateResponse("control.html", {"request": request})

@router.post("/run", response_class=JSONResponse)
async def run_instruction(instruction: str = Form(...)):
    result = control_agent.run(instruction)
    return {"status": "ok", "output": result}