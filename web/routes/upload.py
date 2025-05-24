from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil
from datetime import datetime
import json

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return {"error": f"Unsupported file type: {ext}"}

    destination = UPLOAD_DIR / file.filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Log the upload
    log_entry = {
        "filename": file.filename,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    log_path = Path("logs/uploads_log.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    return {
        "filename": file.filename,
        "status": "uploaded",
        "type": ext,
        "path": str(destination)
    }
