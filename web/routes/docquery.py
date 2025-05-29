from fastapi import APIRouter, Query, Body, Request
from fastapi.responses import PlainTextResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from web.memory.document_retriever import retrieve_similar_documents
from web.memory.agents.dev_assistant import DevAssistantAgent
from web.memory.memory_manager import MemoryManager
from datetime import datetime
from pathlib import Path
import json
import time
import logging
from web.utils.response import success_response, error_response

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]

router = APIRouter()
memory = MemoryManager()

@router.get("/docs/query", response_class=PlainTextResponse)
async def query_documents(prompt: str = Query(..., description="What would you like to ask the documents?")):
    top_docs = retrieve_similar_documents(prompt, top_k=3)
    logger.info("GET /docs/query: Received prompt: %s", prompt)
    if not top_docs:
        logger.warning("No documents found for prompt: %s", prompt)
        return "No processed documents available for query."

    context = "\n\n".join(f"[{doc['filename']}]\n{doc['content']}" for doc in top_docs)
    full_prompt = f"Answer the question based on the following documents:\n\n{context}\n\nQuestion: {prompt}"

    agent = DevAssistantAgent()
    return agent.run_prompt(full_prompt)

class DocQuery(BaseModel):
    query: str = Field(..., min_length=3, description="User query string")
    model: str = "openai"

@router.post("/docquery", response_class=JSONResponse)
async def query_documents_json(data: DocQuery):
    model = data.model if data.model in ["openai", "gemini"] else "openai"
    top_docs = retrieve_similar_documents(data.query, top_k=3)

    if not top_docs:
        logger.warning("POST /docquery: No top documents found for query: %s", data.query)
        return error_response("No documents found.", status_code=404)

    context = "\n\n".join(f"[{doc['filename']}]\n{doc['content']}" for doc in top_docs)
    full_prompt = f"Answer the question based on the following documents:\n\n{context}\n\nQuestion: {data.query}"

    agent = DevAssistantAgent()
    result = agent.run_prompt(full_prompt, model=model)

    logger.info("POST /docquery: Model: %s | Query: %s", model, data.query)
    logger.info("POST /docquery: Response length: %d characters", len(result))

    memory.store_log_entry({
        "text": data.query,
        "response": result,
        "model": model,
        "source": "docquery"
    })

    return success_response({
        "query": data.query,
        "model": model,
        "response": result,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@router.post("/docquery/fake-stream", response_class=StreamingResponse)
async def fake_stream_docquery(data: DocQuery) -> StreamingResponse:
    # NOTE: This is a simulated stream. To support real streaming, replace with an async generator tied to an LLM stream API.
    model = data.model if data.model in ["openai", "gemini"] else "openai"
    top_docs = retrieve_similar_documents(data.query, top_k=3)

    context = "\n\n".join(f"[{doc['filename']}]\n{doc['content']}" for doc in top_docs) if top_docs else "No relevant documents found."
    full_prompt = f"Answer the question based on the following documents:\n\n{context}\n\nQuestion: {data.query}"
    
    agent = DevAssistantAgent()
    full_response = agent.run_prompt(full_prompt, model=model)

    def event_stream():
        for word in full_response.split():
            yield f"data: {word} \n\n"
            time.sleep(0.05)
        yield "data: [DONE]\n\n"

    logger.info("POST /docquery/fake-stream: Simulating stream for model %s with query: %s", model, data.query)
    return StreamingResponse(event_stream(), media_type="text/event-stream")