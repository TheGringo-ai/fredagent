from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from web.utils.diagnostics import diagnose_traceback

router = APIRouter()

class ErrorRequest(BaseModel):
    traceback: str

@router.post("/diagnose-error")
async def diagnose_error(data: ErrorRequest):
    if not data.traceback.strip():
        raise HTTPException(status_code=400, detail="Empty traceback provided.")
    try:
        return diagnose_traceback(data.traceback)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to diagnose error: {str(e)}")
