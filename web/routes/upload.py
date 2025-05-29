from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import shutil
from datetime import datetime
from fastapi.responses import JSONResponse
import json
from web.memory.memory_manager import MemoryManager
from web.utils.response import success_response, error_response

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

memory = MemoryManager()

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return error_response(f"Unsupported file type: {ext}", status_code=400)

    destination = UPLOAD_DIR / file.filename
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        log_entry = {
            "filename": file.filename,
            "text": f"Uploaded file: {file.filename}",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        memory.store_log_entry(log_entry)

        return success_response({
            "filename": file.filename,
            "status": "uploaded",
            "type": ext,
            "path": str(destination)
        })
    except Exception as e:
        return error_response(str(e), status_code=500)

@router.post("/upload/multiple")
async def upload_multiple(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            results.append({
                "filename": file.filename,
                "error": f"Unsupported file type: {ext}"
            })
            continue

        destination = UPLOAD_DIR / file.filename
        try:
            with destination.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            log_entry = {
                "filename": file.filename,
                "text": f"Uploaded file: {file.filename}",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            memory.store_log_entry(log_entry)

            results.append({
                "filename": file.filename,
                "status": "uploaded",
                "type": ext,
                "path": str(destination)
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    return success_response(results)
