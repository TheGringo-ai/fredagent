from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from web.memory.loggerquery import get_recent_logs
from web.memory.summarizer_engine import Summarizer
from web.memory.memory_manager import MemoryManager
from dateutil.parser import parse as parse_date
import json
from web.utils.response import error_response

router = APIRouter()

@router.get("/log/query", response_class=StreamingResponse)
async def summarize_logs(
    request: Request,
    limit: int = 20,
    source: str = "user_log",
    format: str = "text",
    ip: str = None,
    event: str = None,
    start: str = None,
    end: str = None,
    keyword: str = None
):
    memory = MemoryManager()
    summarizer = Summarizer()
    try:
        entries = get_recent_logs(limit * 3)
        if ip:
            entries = [e for e in entries if e.get("data", {}).get("ip") == ip or e.get("ip") == ip]
        if event:
            entries = [e for e in entries if e.get("event") == event]
        if start:
            dt_start = parse_date(start)
            entries = [e for e in entries if "timestamp" in e and parse_date(e["timestamp"]) >= dt_start]
        if end:
            dt_end = parse_date(end)
            entries = [e for e in entries if "timestamp" in e and parse_date(e["timestamp"]) <= dt_end]
        if keyword:
            keyword_lower = keyword.lower()
            entries = [e for e in entries if keyword_lower in json.dumps(e).lower()]
        entries = entries[-limit:]
    except ValueError as e:
        return StreamingResponse((line for line in [f"error: {str(e)}"]), media_type="text/plain")

    prompt = memory.build_context_from_logs(entries)
    summary = summarizer.summarize(prompt)
    return StreamingResponse((line for line in [summary]), media_type="text/plain")
