from fastapi import Query
from datetime import datetime
from fastapi import Request, Form, APIRouter, Query, Body
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

import asyncio
import time
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parents[2]

templates = Jinja2Templates(directory="web/templates")

from web.memory.vector_retriever import retrieve_similar_logs
from web.memory.agents.dev_assistant import DevAssistantAgent
from web.utils.response import success_response, error_response
from web.utils.logger import log_to_file

router = APIRouter()

@router.get("/log/query", response_class=PlainTextResponse)
async def query_log(prompt: str = Query(..., description="What would you like to know?")):
    agent = DevAssistantAgent()

    similar_logs = retrieve_similar_logs(prompt)
    if not similar_logs:
        return "No similar logs found. Try adding more data."

    context = "\n".join(f"{entry['prompt']} => {entry.get('response', '')}" for entry in similar_logs)
    full_prompt = (
        f"You are reviewing past user logs based on a new question: '{prompt}'.\n"
        f"Context from similar logs:\n{context}\n\n"
        f"Based on this, give your best answer."
    )

    return success_response(agent.run_prompt(full_prompt))

@router.get("/devchat", response_class=HTMLResponse)
async def get_devchat(request: Request):
    return templates.TemplateResponse("devchat.html", {
        "request": request,
        "title": "Dev Assistant",
        "chat_log": ""
    })

@router.post("/devchat", response_class=HTMLResponse)
async def post_devchat(request: Request, prompt: str = Form(...), model: str = Form("openai")):
    agent = DevAssistantAgent()
    response = agent.run_prompt(prompt=prompt, model=model)

    return templates.TemplateResponse("devchat.html", {
        "request": request,
        "title": "Dev Assistant",
        "chat_log": f"Prompt: {prompt}\n\nResponse:\n{response}"
    })


# New route: /devchat/query
@router.post("/devchat/query", response_class=JSONResponse)
async def devchat_query(data: dict = Body(...)):
    from datetime import datetime

    prompt = data.get("prompt", "").strip()
    model = data.get("model", "openai")
    session_id = data.get("session_id", "anonymous")

    if not prompt:
        return error_response("Missing prompt", status_code=400)

    agent = DevAssistantAgent()
    response = agent.run_prompt(prompt=prompt, model=model)

    log_entry = {
        "prompt": prompt,
        "model": model,
        "response": response,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": agent.name,  # for traceability
        "session_id": session_id
    }

    log_to_file(log_entry, filename="devchat_log.jsonl")

    return success_response(log_entry)

@router.post("/devchat/stream")
async def stream_devchat(data: dict = Body(...)):
    from datetime import datetime
    import json

    prompt = data.get("prompt", "").strip()
    model = data.get("model", "openai")
    session_id = data.get("session_id", "anonymous")

    if not prompt:
        async def error_stream():
            yield "data: error: Missing prompt\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    agent = DevAssistantAgent()
    full_response = agent.run_prompt(prompt=prompt, model=model)

    # Enhanced logging of streamed interaction
    log_entry = {
        "prompt": prompt,
        "model": model,
        "response": full_response,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": agent.name,
        "session_id": session_id
    }
    log_to_file(log_entry, filename="devchat_log.jsonl")

    async def event_stream():
        chunk = ""
        for word in full_response.split():
            chunk += word + " "
            if len(chunk) > 40:
                yield f"data: {chunk.strip()}\n\n"
                chunk = ""
        if chunk:
            yield f"data: {chunk.strip()}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# New route: /devchat/logs/filter
@router.get("/devchat/logs/filter", response_class=JSONResponse)
async def filter_devchat_logs(
    session_id: str = Query(None),
    agent: str = Query(None),
    start_time: str = Query(None),
    end_time: str = Query(None),
    contains: str = Query(None)
):
    log_path = BASE_DIR / "logs" / "devchat_log.jsonl"
    if not log_path.exists():
        return success_response([])

    results = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                log = json.loads(line)
                if session_id and log.get("session_id") != session_id:
                    continue
                if agent and log.get("agent") != agent:
                    continue
                if contains and contains.lower() not in json.dumps(log).lower():
                    continue
                if start_time:
                    log_time = datetime.fromisoformat(log.get("timestamp", "").replace("Z", ""))
                    if log_time < datetime.fromisoformat(start_time):
                        continue
                if end_time:
                    log_time = datetime.fromisoformat(log.get("timestamp", "").replace("Z", ""))
                    if log_time > datetime.fromisoformat(end_time):
                        continue
                results.append(log)
            except Exception:
                continue

    return success_response({
        "meta": {"count": len(results)},
        "logs": results
    })