from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from memory.agents.dev_assistant import DevAssistantAgent
from pathlib import Path
from datetime import datetime
import json

router = APIRouter()
agent = DevAssistantAgent()

@router.get("/log/query", response_class=StreamingResponse)
async def summarize_logs(request: Request, limit: int = 20, source: str = "user_log"):
    log_path = Path(f"logs/{source}.jsonl")
    if not log_path.exists():
        return StreamingResponse(iter([f"❌ Log file `{source}.jsonl` not found.\n"]), media_type="text/plain")

    try:
        with log_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
            entries = [json.loads(line) for line in lines if line.strip()]
    except json.JSONDecodeError as e:
        return StreamingResponse(iter([f"❌ Failed to parse logs: {e}\n"]), media_type="text/plain")
    except Exception as e:
        return StreamingResponse(iter([f"❌ Failed to read logs: {e}\n"]), media_type="text/plain")

    if not entries:
        return StreamingResponse(iter([f"ℹ️ No entries found in `{source}.jsonl`.\n"]), media_type="text/plain")

    prompt = (
        f"Summarize the last {limit} log entries from `{source}.jsonl`.\n"
        "Focus on patterns, problems, and recurring topics:\n\n"
        + "\n".join(json.dumps(entry) for entry in entries)
    )

    header = (
        f"📄 Summary for `{source}.jsonl`\n"
        f"🕒 Timestamp: {datetime.utcnow().isoformat()}Z\n"
        f"📈 Last {limit} entries requested from {request.client.host}\n\n"
    )

    # Log the query event
    query_log = {
        "event": "log_query",
        "source": source,
        "limit": limit,
        "ip": request.client.host,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    query_log_path = Path("logs/query_log.jsonl")
    query_log_path.parent.mkdir(parents=True, exist_ok=True)
    with query_log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(query_log) + "\n")

    def stream():
        yield header
        try:
            for chunk in agent.run_streaming(prompt):
                yield chunk
        except Exception as e:
            yield f"\n⚠️ LLM failed: {e}\n"
            for line in entries:
                yield json.dumps(line) + "\n"

    return StreamingResponse(stream(), media_type="text/plain")
