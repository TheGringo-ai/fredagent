

from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
import json
from pathlib import Path

router = APIRouter()

TASKBOARD_PATH = Path("web/memory/taskboard_plans.json")

@router.post("/taskboard/save")
async def save_to_taskboard(
    plan_id: str = Form(...),
    plan_text: str = Form(...)
):
    if not TASKBOARD_PATH.exists():
        taskboard = {}
    else:
        with TASKBOARD_PATH.open("r", encoding="utf-8") as f:
            taskboard = json.load(f)

    taskboard[plan_id] = {
        "text": plan_text,
        "source": "fredai"
    }

    with TASKBOARD_PATH.open("w", encoding="utf-8") as f:
        json.dump(taskboard, f, indent=2)

    return RedirectResponse(url="/chat", status_code=303)