from fastapi import APIRouter
from pydantic import BaseModel
from web.memory.summarizer_engine import Summarizer
from web.memory.memory_manager import MemoryManager
from web.utils.response import success_response, error_response

router = APIRouter()
summarizer = Summarizer()
memory = MemoryManager()

class SummaryRequest(BaseModel):
    text: str
    max_length: int = 130
    min_length: int = 30
    return_intent: bool = False

@router.post("/summarize")
async def summarize_text(request: SummaryRequest):
    print(f"Received summary request: {request.text[:60]}...")

    if len(request.text.split()) < 5:
        return success_response({"summary": "[Text too short to summarize]"})

    summary = summarizer.summarize(
        text=request.text,
        max_length=request.max_length,
        min_length=request.min_length
    )

    print(f"Summary generated: {summary[:60]}...")

    response = {"summary": summary}

    if request.return_intent:
        intent = memory.classify_intent(request.text)
        response["intent"] = intent
        print(f"Intent classified: {intent}")

    return success_response(response)

@router.get("/summarize")
async def get_summary_sample():
    return success_response({"message": "POST to /summarize with {'text': '...'} to receive a summary."})
