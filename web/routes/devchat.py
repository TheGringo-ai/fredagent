from fastapi import Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="web/templates")
from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse
from memory.vector_retriever import retrieve_similar_logs
from memory.agents.dev_assistant import DevAssistantAgent

router = APIRouter()

from fastapi import Body
from fastapi.responses import JSONResponse

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

    return agent.run_prompt(full_prompt)
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
    from pathlib import Path
    import json

    prompt = data.get("prompt", "").strip()
    model = data.get("model", "openai")

    if not prompt:
        return JSONResponse(status_code=400, content={"error": "Missing prompt"})

    agent = DevAssistantAgent()
    response = agent.run_prompt(prompt=prompt, model=model)

    log_entry = {
        "prompt": prompt,
        "model": model,
        "response": response,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    log_path = Path("logs/devchat_log.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    return log_entry

from fastapi.responses import StreamingResponse
import time

@router.post("/devchat/stream", response_class=StreamingResponse)
async def stream_devchat(data: dict = Body(...)):
    prompt = data.get("prompt", "").strip()
    model = data.get("model", "openai")

    if not prompt:
        yield "data: Missing prompt\n\n"
        return

    agent = DevAssistantAgent()
    full_response = agent.run_prompt(prompt=prompt, model=model)

    def event_stream(text):
        for word in text.split():
            yield f"data: {word} \n\n"
            time.sleep(0.05)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(full_response), media_type="text/event-stream")