


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from web.db import get_db
from web.models import User, PromptLog, MemoryEvent
from pydantic import BaseModel
from web.utils.response import success_response, error_response

router = APIRouter(prefix="/models", tags=["Models API"])

class UserCreate(BaseModel):
    name: str

class PromptCreate(BaseModel):
    prompt: str

class MemoryCreate(BaseModel):
    event: str

@router.post("/users")
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == data.name).first()
    if user:
        return success_response({"user_id": user.id, "name": user.name})
    user = User(name=data.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return success_response({"user_id": user.id, "name": user.name})

@router.post("/users/{user_id}/prompts")
def add_prompt(user_id: int, data: PromptCreate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    prompt = PromptLog(prompt=data.prompt, user_id=user_id)
    db.add(prompt)
    db.commit()
    return success_response({"prompt_id": prompt.id, "timestamp": prompt.timestamp})

@router.post("/users/{user_id}/memory")
def add_memory(user_id: int, data: MemoryCreate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    memory = MemoryEvent(event=data.event, user_id=user_id)
    db.add(memory)
    db.commit()
    return success_response({"memory_id": memory.id, "timestamp": memory.timestamp})

@router.get("/users/{user_id}/history/prompts")
def get_prompt_history(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    prompts = db.query(PromptLog).filter_by(user_id=user_id).order_by(PromptLog.timestamp.desc()).limit(10).all()
    return success_response([{"prompt": p.prompt, "timestamp": p.timestamp} for p in prompts])

@router.get("/users/{user_id}/history/memory")
def get_memory_history(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    events = db.query(MemoryEvent).filter_by(user_id=user_id).order_by(MemoryEvent.timestamp.desc()).limit(10).all()
    return success_response([{"event": e.event, "timestamp": e.timestamp} for e in events])