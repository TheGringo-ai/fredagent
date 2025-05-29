from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from web.utils.response import success_response, error_response
from pydantic import BaseModel
from web.memory.summarizer_engine import Summarizer

router = APIRouter()

class ReflectionRequest(BaseModel):
    chat_history: list[str]

@router.post("/reflect")
async def reflect_on_chat(data: ReflectionRequest, request: Request):
    try:
        summarizer = Summarizer()
        chat_text = "\n".join(data.chat_history)
        insight = summarizer.summarize_text(chat_text)
        return success_response({"reflection": insight})
    except Exception as e:
        return error_response(str(e), status_code=500)