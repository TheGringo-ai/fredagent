from fastapi import APIRouter
from pydantic import BaseModel, constr, conint
from datetime import datetime
from pathlib import Path
import json

router = APIRouter()

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "user_log.jsonl"

class User(BaseModel):
    name: constr(min_length=2)
    age: conint(ge=0, le=120)

@router.post("/user")
def create_user(user: User):
    timestamp = datetime.utcnow().isoformat() + 'Z'
    log_entry = {
        "status": "ok",
        "user": user.dict(),
        "timestamp": timestamp
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
    return log_entry