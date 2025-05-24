from fastapi import APIRouter, Query
from fastapi.responses import PlainTextResponse
from memory.document_retriever import retrieve_similar_documents
from memory.agents.dev_assistant import DevAssistantAgent
from fastapi import Body
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
import time

router = APIRouter()

@router.get("/docs/query", response_class=PlainTextResponse)
async def query_documents(prompt: str = Query(..., description="What would you like to ask the documents?")):
    top_docs = retrieve_similar_documents(prompt, top_k=3)

    if not top_docs:
        return "No processed documents available for query."

    context = "\n\n".join(f"[{doc['filename']}]\n{doc['content']}" for doc in top_docs)
    full_prompt = f"Answer the question based on the following documents:\n\n{context}\n\nQuestion: {prompt}"

    agent = DevAssistantAgent()
    return agent.run_prompt(full_prompt)

class DocQuery(BaseModel):
    query: str
    model: str = "openai"

@router.post("/docquery", response_class=JSONResponse)
async def query_documents_json(data: DocQuery):
    from datetime import datetime
    from pathlib import Path
    import json

    model = data.model if data.model in ["openai", "gemini"] else "openai"
    top_docs = retrieve_similar_documents(data.query, top_k=3)

    if not top_docs:
        return JSONResponse(content={"error": "No documents found."}, status_code=404)

    context = "\n\n".join(f"[{doc['filename']}]\n{doc['content']}" for doc in top_docs)
    full_prompt = f"Answer the question based on the following documents:\n\n{context}\n\nQuestion: {data.query}"

    agent = DevAssistantAgent()
    result = agent.run_prompt(full_prompt, model=model)

    log_entry = {
        "query": data.query,
        "model": model,
        "response": result,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    log_path = Path("logs/docquery_log.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    return log_entry

@router.post("/docquery/stream", response_class=StreamingResponse)
async def stream_docquery(data: DocQuery):
    model = data.model if data.model in ["openai", "gemini"] else "openai"
    top_docs = retrieve_similar_documents(data.query, top_k=3)

    if not top_docs:
        yield "data: No relevant documents found.\n\n"
        return

    context = "\n\n".join(f"[{doc['filename']}]\n{doc['content']}" for doc in top_docs)
    full_prompt = f"Answer the question based on the following documents:\n\n{context}\n\nQuestion: {data.query}"

    agent = DevAssistantAgent()
    full_response = agent.run_prompt(full_prompt, model=model)

    def event_stream(text):
        for word in text.split():
            yield f"data: {word} \n\n"
            time.sleep(0.05)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(full_response), media_type="text/event-stream")