"""
Route: /user
Description: Accepts validated user input, logs data with timestamp, and returns confirmation.
Dependencies: Memory integration enabled.
"""
from fastapi import APIRouter
from pydantic import BaseModel, constr, conint
from datetime import datetime
from pathlib import Path
import json
from typing import Optional

from web.memory.memory_manager import MemoryManager
from web.utils.response import success_response

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "user_log.jsonl"

class User(BaseModel):
    name: constr(min_length=2)
    age: conint(ge=0, le=120)
    email: Optional[str] = None

    def __repr__(self):
        return f"User(name={self.name}, age={self.age}, email={self.email})"

memory = MemoryManager()

@router.post("/user")
def create_user(user: User):
    timestamp = datetime.utcnow().isoformat() + 'Z'
    prompt_text = f"{user.name}, {user.age}" + (f", {user.email}" if user.email else "")

    log_entry = {
        "status": "ok",
        "user": user.dict(),
        "text": prompt_text,
        "timestamp": timestamp
    }

    def log_entry_repr(self):
        return f"LogEntry(status={self['status']}, user={self['user']}, text={self['text']}, timestamp={self['timestamp']})"
    log_entry.__repr__ = log_entry_repr.__get__(log_entry)

    memory.store_log_entry(log_entry)

    similar_logs = memory.retrieve_similar(prompt_text, top_k=3)
    print("[MEMORY] Top 3 similar logs:")
    for log in similar_logs:
        print(log)

    return success_response(log_entry)