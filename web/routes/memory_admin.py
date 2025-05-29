from fastapi import APIRouter
from pathlib import Path
import json
import os
from web.memory.plan_executor import store_plan
from web.utils.response import success_response, error_response
from web.memory.embedding_store import get_store_summary
from web.memory.loggerquery import get_recent_logs

router = APIRouter(prefix="/memory", tags=["Memory Admin"])

@router.get("/status")
async def memory_status():
    return success_response({"status": "Memory admin endpoint active"})

@router.get("/logs")
async def get_memory_logs():
    log_file = Path("logs/user_log.jsonl")
    if not log_file.exists():
        return success_response({"logs": []})
    
    with open(log_file, "r") as f:
        lines = f.readlines()
    
    return success_response({"logs": [json.loads(line) for line in lines[-50:]]})

@router.delete("/plans/clear")
async def clear_plans():
    store_plan("cleared", {})
    return success_response({"status": "All plans cleared using plan_executor"})

@router.get("/system")
async def system_health():
    return success_response({
        "status": "ok",
        "env": os.environ.get("ENV", "dev"),
        "memory_log_exists": Path("logs/user_log.jsonl").exists(),
        "embedding_store": get_store_summary()
    })

@router.get("/logs/recent")
async def get_recent_memory_logs(
    limit: int = 50,
    skip: int = 0,
    contains: str = None
):
    logs_data = get_recent_logs(limit=limit + skip)
    filtered_logs = []

    if contains:
        for entry in logs_data["logs"]:
            if contains.lower() in json.dumps(entry).lower():
                filtered_logs.append(entry)
    else:
        filtered_logs = logs_data["logs"]

    paginated_logs = filtered_logs[skip:skip + limit]

    return success_response({
        "count": len(paginated_logs),
        "logs": paginated_logs
    })
